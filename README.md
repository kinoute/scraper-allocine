# Scraper Allociné

Just a random scraper to retrieve some datas about movies listed on Allociné.fr.

The script will save movie datas available on the http://www.allocine.fr/films webpage as a `.csv` file.

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
docker build -t allocine .
# or "make build"
```

## Usage


By default, the script will:

* Scrap the first 50 pages of Allociné ;
* Wait 10 seconds between each page scraped ;
* Save the results in a csv filename called `allocine.csv` in the `files` folder.

To run the script with these default options, simply do:

```bash
docker run --rm -it --name "allocine" -v files:/allocine/files allocine
# or make start
```

### Change default options

The script has 3 customizable options that can be changed through the command line when running the container:

* **The number of pages to scrap:** with the `-p` or `—pages` argument (Default: 50) ;
* **The time in sec to wait before each page is scraped:** with the `-t`or `—timeout` argument (Default: 10) ;
* **The CSV filename where results will be stored:** with the `-d` or `—dataset` argument (Default: `allocine.csv`).

For example, if we wanted to scrap 100 pages instead of 50 with 30 secondes between each page and store the results in a CSV file called `results.csv`, we will do:

```bash
# note that we added the name of the python file in the docker command
docker run --rm -it --name "allocine" -v files:/allocine/files allocine scraper.py -p 100 -t 30 -d results.csv
```

The script automatically update and save the results after every page scraped. If for whatever reason, you want to stop the scraping, just do `CTRL+C`in your Terminal.

## Abuse

This script was just made for fun to play around with BeautifulSoup and Python. Please don't use to do bad things and ruin Allociné servers!
