"""Scraps various informations about movies on Allocine.fr

Attributes:
    scraper (object): Instance of the main class.
"""

import bs4
from bs4 import BeautifulSoup
import pandas as pd
import psycopg2
import dateparser

import requests
import re
import os
import time
import logging
from typing import Union
import psycopg2
import dateparser
import datetime

# better logging
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="[%(asctime)s] %(message)s")

# load and get environment variables
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class AlloCineScraper(object):

    """Main class to scrap movies from Allociné.fr

    Attributes:
        allocine_url (str): Base URL where we will get movie attributes.
        dataset (pd.DataFrame): Pandas DataFrame with all the scraped informations.
        dataset_name (str): CSV Filename of the Pandas DataFrame that hosts all our movie results.
        db_conn (object): Connection to our postgres database through psycopg2.
        db_cursor (object): Cursor to our postgres database through our psycopg2's connection.
        human_pause (int): Time to wait before each page scraped.
        movie_infos (list): List of movie attributes we're interested in.
        number_of_pages (int): How many pages to scrap on Allociné.fr.
    """

    allocine_url = "https://www.allocine.fr/films/?page="
    movie_infos = [
        "id",
        "title",
        "release_date",
        "duration",
        "genres",
        "directors",
        "actors",
        "press_rating",
        "spec_rating",
        "summary",
    ]

    # store the full movie results
    dataset = pd.DataFrame(columns=movie_infos)

    def __init__(
        self,
        number_of_pages: int = 50,
        dataset_name: str = "allocine.csv",
        human_pause: int = 10,
    ) -> None:
        """Initializes our Scraper class.

        Args:
            number_of_pages (int, optional): How many pages to scrap on Allociné.fr. Default: 50.
            dataset_name (str, optional): Filename of the Pandas DataFrame as CSV. Default: allocine.csv
            human_pause (int, optional): Time to wait before each page scraped. Default: 10 sec.

        Raises:
            Exception: Exists the scraper if the arguments are not appropriate.
        """

        if not isinstance(number_of_pages, int) or number_of_pages < 2:
            raise Exception("number_of_pages must be an integer superior to 1.")

        self.number_of_pages = number_of_pages

        if not isinstance(dataset_name, str) or dataset_name[-4:] != ".csv":
            raise Exception("dataset_name must have a valid CSV name.")

        self.dataset_name = dataset_name

        if not isinstance(human_pause, int) or human_pause < 2:
            raise Exception("human_pause must be an integer superior to 1.")

        self.human_pause = human_pause

        # let's connect to the postgres database, shall we?
        self.db_conn = psycopg2.connect(
            host="db",
            dbname=os.getenv("POSTGRES_USER"),
            user=os.getenv("POSTGRES_USER"),
        )

        # psycopg2 cursor
        self.db_cursor = self.db_conn.cursor()

        logging.info("Initializing Allocine Scraper..")
        logging.info("- Number of pages to scrap: %d", self.number_of_pages)
        logging.info("- Time to wait between pages: %d sec", self.human_pause)
        logging.info("- Results will be stored in: %s", self.dataset_name)

    def _get_page(self, page_number: int) -> requests.models.Response:
        """Private method to get the full content of a webpage.

        Args:
            page_number (int): Number of the page on Allociné.fr.

        Returns:
            requests.models.Response: Full source code of the asked webpage.
        """

        response = requests.get(self.allocine_url + str(page_number))
        return response

    def start_scraping_movies(self) -> None:
        """Starts the scraping process.
        """

        logging.info("Starting scraping movies from Allocine...")

        for number in range(1, self.number_of_pages):

            logging.info(f"Fetching Page {number}/{self.number_of_pages}")

            # get the plain text source code of the page
            response = self._get_page(number)

            # parse each page results and get attributes
            self._parse_list_page(response)

            logging.info(
                f"Done scraping page #{number}. Waiting {self.human_pause} sec before the next one.."
            )

            # let's look a fucking human being
            time.sleep(self.human_pause)

        # we're done here, closing postgres connection
        self.db_cursor.close()
        self.db_conn.close()

        logging.info("Done scraping Allocine.")
        logging.info(f"Results are stored in {self.dataset_name}.")

    def _parse_list_page(self, page: requests.models.Response) -> None:
        """Private method to parse a single result page from Allociné.fr.

        Args:
            page (str): Source code of a Allocine.fr webpage.
        """

        parser = BeautifulSoup(page.content, "html.parser")

        # iterate through each "movie" card
        for movie in parser.find_all("li", class_="mdl"):

            # store temporarly all the movie datas
            movie_datas = []

            # get every info we're interested in
            for info in self.movie_infos:

                # take care of unavailable infos for some movies
                try:
                    scraped_info = getattr(self, "_get_movie_" + info)(movie)
                except:
                    scraped_info = None

                # store the movie attribute
                movie_datas.append(scraped_info)

            # add movie infos to the dataframe
            self.dataset.loc[len(self.dataset)] = movie_datas

            # add movie infos to the postgres database
            self._insert_movie_to_db(movie_datas)

        # just to be safe, save after every page
        self.dataset.to_csv("files/" + self.dataset_name, index=False)

    def _insert_movie_to_db(self, movie_datas) -> None:
        """Private method to insert an individual movie to the postgres db.

        Args:
            movie_datas (list): The movie datas we just scraped.
        """

        self.db_cursor.execute(
            """INSERT INTO public.movies
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            tuple(movie_datas),
        )

        self.db_conn.commit()

    def _get_movie_id(self, movie: bs4.element.Tag) -> int:
        """Private method to retrieve the movie ID according to Allociné.

        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.

        Returns:
            int: The movie ID according to Allociné.
        """

        movie_id = re.sub(
            r"\D", "", movie.find("div", {"class": "content-title"}).a["href"]
        )

        return int(movie_id)

    def _get_movie_title(self, movie: bs4.element.Tag) -> str:
        """Private method to retrieve the movie title.

        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.

        Returns:
            str: The movie title.
        """

        movie_title = movie.find("div", {"class": "content-title"}).text.strip()

        return movie_title

    def _get_movie_release_date(self, movie: bs4.element.Tag) -> datetime.datetime:
        """Private method to retrieve the movie release date.

        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.

        Returns:
            str: The movie release date.
        """

        movie_date = movie.find("span", {"class": "date"}).text.strip()
        movie_date = dateparser.parse(movie_date, date_formats=["%d %B %Y"])
        return movie_date

    def _get_movie_duration(self, movie: bs4.element.Tag) -> str:
        """Private method to retrieve the movie duration.

        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.

        Returns:
            str: The movie duration.
        """

        movie_duration = movie.find("span", {"class": "spacer"}).next_sibling.strip()

        return movie_duration

    def _get_movie_genres(self, movie: bs4.element.Tag) -> str:
        """Private method to retrieve the movie genre(s).

        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.

        Returns:
            str: The movie genre(s).
        """

        movie_genres = [
            genre.text
            for genre in movie.find(
                "div", {"class": "meta-body-item meta-body-info"}
            ).find_all(
                "span", class_=re.compile(r".*==$"),
            )
        ]

        return ", ".join(movie_genres)

    def _get_movie_directors(self, movie: bs4.element.Tag) -> str:
        """Private method to retrieve the movie director(s).

        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.

        Returns:
            str: The movie director(s).
        """

        movie_directors = [
            link.text
            for link in movie.find(
                "div", {"class": "meta-body-item meta-body-directmaision light"}
            ).find_all(["a", "span"], class_=re.compile(r".*blue-link$"))
        ]

        return ", ".join(movie_directors)

    def _get_movie_actors(self, movie: bs4.element.Tag) -> str:
        """Private method to retrieve the movie actor(s).

        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.

        Returns:
            str: The movie actor(s).
        """

        movie_actors = [
            actor.text
            for actor in movie.find(
                "div", {"class": "meta-body-item meta-body-actor light"}
            ).find_all(["a", "span"])
        ][1:]

        return ", ".join(movie_actors)

    def _get_movie_press_rating(self, movie: bs4.element.Tag) -> Union[float, None]:
        """Private method to retrieve the movie rating according to the press.

        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.

        Returns:
            Union[float, None]: The movie rating according to the press.
        """

        # get all the available ratings
        movie_ratings = movie.find_all("div", class_="rating-item")

        for ratings in movie_ratings:

            if "Presse" in ratings.text:
                return float(
                    re.sub(
                        ",", ".", ratings.find("span", {"class": "stareval-note"}).text
                    )
                )
        return None

    def _get_movie_spec_rating(self, movie: bs4.element.Tag) -> Union[float, None]:
        """Private method to retrieve the movie rating according to the spectators.

        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.

        Returns:
            Union[float, None]: The movie rating according to the spectators.
        """

        # get all the available ratings
        movie_ratings = movie.find_all("div", class_="rating-item")

        for ratings in movie_ratings:

            if "Spectateurs" in ratings.text:
                return float(
                    re.sub(
                        ",", ".", ratings.find("span", {"class": "stareval-note"}).text
                    )
                )

        return None

    def _get_movie_summary(self, movie: bs4.element.Tag) -> str:
        """Private method to retrieve the movie summary.

        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.

        Returns:
            str: The movie summary.
        """

        movie_summary = movie.find("div", {"class": "synopsis"}).text.strip()

        return movie_summary


if __name__ == "__main__":

    scraper = AlloCineScraper(
        number_of_pages=int(os.getenv("NUM_PAGES")),
        dataset_name=os.getenv("DATASET_NAME"),
        human_pause=int(os.getenv("TIMEOUT")),
    )

    scraper.start_scraping_movies()
