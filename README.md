# Scraper Allociné

Just a random scraper to retrieve some datas about movies listed on Allociné.fr.

The script will save movie datas available on the http://www.allocine.fr/films webpage as a `.csv` file and in a postgres database.

## Movies informations scraped

The movie attributes retrieved when available are:

* The movie ID ;

* The title ;

* The release date ;

* The duration ;

* The genre(s) ;

* The director(s) ;

* The main actor(s) ;

* The press rating ;

* The spectators rating ;

* The movie Summary.


## Installation

First, clone the repository:

```bash
git clone git@github.com:kinoute/scraper-allocine.git
```

Go to the folder and build the container:

```bash
docker-compose build
# or "make build"
```

## Usage

First, you have to rename the `.env.dist` template file to `.env`. Then fill it with your own values. At first start, the postgres environment variables will be used to create the postgres server.

By default, the script will:

* Scrap the first 50 pages of Allociné ;
* Save every movie to the postgres database in its own container ;
* Wait 10 seconds between each page scraped ;
* Save the full results in a csv filename called `allocine.csv` in the `files` folder.

To run the script with these default options, simply do:

```bash
docker-compose up --build
# or make start
```

### Change default options

The script has 3 customizable options that can be changed in the `.env` file:

* **The number of pages to scrap** (Default: 50) ;
* **The time in sec to wait before each page is scraped** (Default: 10) ;
* **The CSV filename where results will be stored** (Default: `allocine.csv`).

## Data

The script automatically update and save the results after every page scraped for the `.csv` file. For postgres, the database is updated on every movie scraped.

If for whatever reason, you want to stop the scraping, just do `Ctrl+C` in your Terminal.

## Abuse

This script was just made for fun to play around with BeautifulSoup and Python. Please don't use to do bad things and ruin Allociné servers!
