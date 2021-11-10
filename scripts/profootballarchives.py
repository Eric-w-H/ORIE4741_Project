import os
import time
from bs4.element import SoupStrainer, Tag
import requests
from bs4 import BeautifulSoup
from requests.models import Response
from requests.sessions import Request
import pandas as pd
import numpy as np


def get_random_delay(delay=3):
    return np.abs(np.random.normal(delay, delay)) + delay


def url_to_code(url):
    if 'nfl' in url:
        return url[7:].split('.')[0]
    elif 'apfa' in url:
        return url[8:].split('.')[0]
    else:
        return url[4:].split('.')[0]


def get_years(url):
    print("[*] Getting years index")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser",
                         parse_only=SoupStrainer(attrs={"id": "years"}))
    years = soup.find_all("a")
    return years


def parse_team(url, team: Tag):
    teamurl = team['href']
    teamtext = team.get_text()
    print('[***] Processing %s' % teamtext)

    response = requests.get(url + teamurl)
    soup = BeautifulSoup(response.text, "html.parser",
                         parse_only=SoupStrainer(attrs={'id': 'scores'}))

    # Exclude exhibition games
    exclusion = soup.find_all(attrs={'class': 'exh'})
    for elem in exclusion:
        elem.extract()

    body = soup.find_all('tr')[1:]  # discard "SCORES"
    stepover = 11

    def get_text(elem): return elem.get_text().strip()
    get_text = np.vectorize(get_text)

    data = get_text(np.array(body)).reshape((-1, stepover)).copy()
    columns = ['Day', 'Date', 'Home/Away', 'Opponent', 'Score',
               'W/L/T', 'Overtime', 'Location', 'Venue', 'Attendance', 'Notes']
    data = data[1:]

    df = pd.DataFrame(data, columns=columns)
    df['Team'] = [teamtext]*len(df)

    # Handle the different home team urls differently
    df['Team Code'] = [url_to_code(teamurl)]*len(df)

    # Get the away team codes
    away_urls = soup.find_all('a')
    opponent_code = []
    for team_url in away_urls:
        opponent_code.append(url_to_code(team_url['href']))

    df['Opponent Code'] = opponent_code
    return df


def parse_year(url, year: Tag, delay=3):
    yearurl = year['href']
    yeartext = year.get_text()

    time.sleep(get_random_delay(delay))
    print('[**] Parsing %s' % yeartext)

    response = requests.get(url + yearurl)
    soup = BeautifulSoup(response.text, "html.parser", parse_only=SoupStrainer(
        attrs={"style": "text-align:left"}))
    links = soup.find_all("a")

    dataframes = []
    for link in links:
        time.sleep(get_random_delay(delay))
        dataframes.append(parse_team(url, link))
    return pd.concat(dataframes).reindex()


def main():
    urlbase = """https://www.profootballarchives.com/"""
    home = "nfl.html"

    filename = "matches.csv"
    path = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    filepath = os.path.join(path, filename)
    filepath = os.path.normpath(filepath)

    dataframes = []
    years = get_years(urlbase + home)
    for year in years:
        if(int(year.string) < 2021):
            tries = 3
            while tries:  # Retry if we get oserrors
                try:
                    dataframes.append(parse_year(urlbase, year, delay=3))
                except OSError as err:
                    print("[**!] ERROR " + str(err) + ", retrying...")
                    time.sleep(2)
                    tries -= 1
                    continue
                break

    print('[*] Writing output to ' + filepath)
    df = pd.concat(dataframes).reindex()
    df.to_csv(filepath)


if(__name__ == "__main__"):
    main()
