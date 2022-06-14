import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
from urllib.error import HTTPError
from pathlib import Path
import os


def get_tutiempo_table(year, month, debug=False):
    """
    Fetch the webpage of the specified year and month, and scrape the data.
    """
    # Get HTML code.
    if debug:
        year = "2022"
        month = "01"

        with open(Path("tutiempo_debug/weather_01-2022.html"), "r") as fp:
            soup = BeautifulSoup(fp, "html.parser")
    else:
        url = f"https://en.tutiempo.net/climate/{month}-{year}/ws-654180.html"

        try:
            page = urllib.request.urlopen(url)
        except HTTPError as e:
            print(f"\t[{year}-{month}]\tNo data available..  ({e.code})")
            return

        soup = BeautifulSoup(page.read(), "html.parser")

    # Get the contents of the main table.
    tables = soup.find_all("table")
    rows = tables[3].find_all("tr")

    # Get the header of the table.
    abbr = rows[0].find_all("abbr")
    headers = [a.get_text() for a in abbr]
    headers.insert(0, "Day")

    # Parse all rows of table.
    data = []
    for row in rows[1:]:
        data.append([td.get_text() for td in row.find_all("td")])

    # Create dataframe from the table.
    # Replace '\xa0' with an empty string, as it is a NBSP.
    # Replace '-' with an empty string, as it is missing data.
    df = pd.DataFrame(data=data, columns=headers)
    df = df.replace({"\xa0": "", "-": ""}, regex=True)

    # Store DataFrame as a CSV.
    df.to_csv(Path(f"tutiempo/{year}/{month}.csv"))


def get_tutiempo(years):
    """
    Download the Tutiempo dataset for the given years through a web scraper.
    """
    for year in years:
        print(f"\nStarting on year {year}..")

        # Create folder for the current years results.
        os.makedirs(Path(f"tutiempo/{year}"), exist_ok=True)

        # Fill year folder with data from all months.
        for month in ["01", "02", "03", "04", "05", "06", "07", "08", "09",
                      "10", "11", "12"]:
            get_tutiempo_table(year, month)


if __name__ == "__main__":
    get_tutiempo(["2022", "2021"])
