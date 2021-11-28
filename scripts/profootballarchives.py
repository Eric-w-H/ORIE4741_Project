import os
import time
from bs4.element import SoupStrainer, Tag
import requests
from bs4 import BeautifulSoup
from requests.models import Response
from requests.sessions import Request
import pandas as pd
import numpy as np
import json


def get_random_delay(delay=3):
    return np.abs(np.random.normal(delay, 1)) + 1.2


def url_to_code(teamurl, leagueurl):
    base_len = len(leagueurl.split('.')[0])
    return teamurl.split('.')[0][base_len:]


def get_years(url):
    print("[*] Getting years index")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser",
                         parse_only=SoupStrainer(attrs={"id": "years"}))
    years = soup.find_all("a")
    return years


def scores(response, leagueurl):
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

    data = get_text(np.array(body, dtype=np.object)
                    ).reshape((-1, stepover)).copy()
    columns = ['Day', 'Date', 'Home/Away', 'Opponent', 'Score',
               'W/L/T', 'Overtime', 'Location', 'Venue', 'Attendance', 'Notes']
    data = data[1:]

    df = pd.DataFrame(data, columns=columns)

    # Get the away team codes
    away_urls = soup.find_all('a')
    opponent_code = []
    for team_url in away_urls:
        opponent_code.append(url_to_code(team_url['href'], leagueurl))

    df['Opponent Code'] = opponent_code
    return df


def stats(response):
    soup = BeautifulSoup(response.text, "html.parser",
                         parse_only=SoupStrainer(attrs={'id': 'stats'}))

    def has_title(tag: Tag): return tag.has_attr('title')

    stats_dict = dict()
    tables = soup.find_all("table")
    for table in tables:
        try:
            category = table.tr.th.string
            print(f'[****] Gathering {category}')

            titles = table.find_all(has_title)
            title_list = ['Totals'] + [title['title'] for title in titles]

            data_list = list()
            data = table.find_all(class_='career')
            for line in data:
                data_list.append(
                    {title: elem.string for title, elem in zip(title_list, line.children)})
            stats_dict[category] = data_list
        except:
            print(f'[***!] Skipping...')
            continue
    return stats_dict


def parse_team(url, team: Tag, leagueurl):
    teamurl = team['href']
    teamtext = team.get_text()
    print('[***] Processing %s' % teamtext)

    response = requests.get(url + teamurl)

    score_df = scores(response, leagueurl)
    stats_dict = stats(response)

    score_df['Team'] = [teamtext]*len(score_df)

    # Handle the different home team urls differently
    team_code = url_to_code(teamurl, leagueurl)
    score_df['Team Code'] = [team_code]*len(score_df)

    return score_df, team_code, stats_dict


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
    stats_agg = dict()
    for link in links:
        time.sleep(get_random_delay(delay))
        df, team, dct = parse_team(url, link, yearurl)
        dataframes.append(df)
        stats_agg[team] = dct

    return pd.concat(dataframes).reindex(), {yeartext: stats_agg}


def main():
    urlbase = """https://www.profootballarchives.com/"""
    home = "nfl.html"

    matches_filename = "matches.csv"
    stats_filename = "stats.json"
    path = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

    stats_filepath = os.path.join(path, stats_filename)
    matches_filepath = os.path.join(path, matches_filename)
    matches_filepath = os.path.normpath(matches_filepath)

    dataframes = []
    stats = []
    years = get_years(urlbase + home)
    for year in years:
        if(int(year.string) < 2021):
            tries = 3
            while tries:  # Retry if we get oserrors
                try:
                    frame, stat = parse_year(urlbase, year, delay=1.1)
                    dataframes.append(frame)
                    stats.append(stat)
                except OSError as err:
                    print("[**!] ERROR " + str(err) + ", retrying...")
                    time.sleep(2)
                    tries -= 1
                    continue
                break

    print('[*] Writing matches to ' + matches_filepath)
    df = pd.concat(dataframes).reindex()
    df.to_csv(matches_filepath)

    print('[*] Writing stats to ' + stats_filepath)
    json_stats = json.dumps({k: v for d in stats for k, v in d.items()})
    with open(stats_filepath, 'w+') as stats_file:
        stats_file.write(json_stats)


if(__name__ == "__main__"):
    main()
