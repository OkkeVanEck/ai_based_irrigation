#!/usr/bin/env python3
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
from urllib.error import HTTPError
from pathlib import Path
import os
from dateutil.relativedelta import relativedelta
from datetime import date
from eto import ETo


def _float(s):
    try:
        return float(s)
    except:
        return None


def _get_tutiempo_table(year, month, debug=False):
    """
    Fetch the webpage of the specified year and month, and scrape the data.
    """
    # Get HTML code.
    if debug:
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

    start = date(year=int(year), month=int(month), day=1)
    end = start + relativedelta(months=1, day=1, days=-1)

    # Parse all rows of table.
    data = []
    for row in rows[1:end.day + 1]:
        data.append([_float(td.get_text()) for td in row.find_all("td")])

    # Create dataframe from the table.
    # Replace '\xa0' with an empty string, as it is a NBSP.
    # Replace '-' with an empty string, as it is missing data.
    df = pd.DataFrame(data=data, columns=headers)
    df.index = pd.date_range(start, end)

    return df


def get_tutiempo(years):
    """
    Download the Tutiempo dataset for the given years through a web scraper.
    """
    full_df = pd.DataFrame()
    for year in years:
        print(f"\nProcessing year {year}..")

        # Create folder for the current years results.
        os.makedirs(Path(f"tutiempo/{year}"), exist_ok=True)

        # Fill year folder with data from all months.
        df = pd.DataFrame()
        for month in ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]:
            df = df.append(_get_tutiempo_table(year, month))

        df = df[['Tm', 'TM', 'T', 'H', 'SLP', 'PP', 'V']]
        df.rename(columns={
            'Tm': 'T_min',  # Min temp
            'TM': 'T_max',  # Max temp
            'T': 'T_mean',  # Average temp
            'H': 'RH_mean',  # Relative humidity
            'SLP': 'P',  # Atmospheric pressure
            'PP': 'Prcp(mm)',  # Total rainfall
            'V': 'U_z'  # Average wind speed
        }, inplace=True)

        df.interpolate(method='time', limit_direction='both', inplace=True)

        # Calculate ETo based on FAO Penman-Monteith equation (z_msl, lat lon in Tamale)
        et = ETo(df, freq='D', z_msl=168, lat=9.5, lon=-0.85)
        df['Et0(mm)'] = et.eto_fao().interpolate(method='time', limit_direction='both').fillna(0)

        # Finalize to output AquaCrop model kan use
        df = df[['T_min', 'T_max', 'Prcp(mm)', 'Et0(mm)']]

        df.rename(columns={
            'T_min': 'MinTemp',
            'T_max': 'MaxTemp',
            'Prcp(mm)': 'Precipitation',
            'Et0(mm)': 'ReferenceET'
        }, inplace=True)

        df.index.name = 'Date'
        df.ReferenceET.clip(lower=0.1, inplace=True)
        full_df = full_df.append(df)

    next_year = full_df.tail(730)
    next_year.index += pd.offsets.DateOffset(months=12)

    full_df = full_df.append(next_year)
    full_df.to_csv('tamale_weather.csv')


if __name__ == "__main__":
    get_tutiempo([f"201{y}" for y in range(10)] +
                 [f"2020", "2021"])
