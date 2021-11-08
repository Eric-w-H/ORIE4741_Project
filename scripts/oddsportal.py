from bs4 import BeautifulSoup
import requests
import time
import os

def get_years(url):
  print("[*] Getting years index")
  response = requests.get(url)
  soup = BeautifulSoup(response.text,"html.parser")
  print(response)
  print(response.text)
  print(soup.find_all("main-filter"))

def main():
  url = """https://www.oddsportal.com/american-football/usa/nfl/results/"""

  filename = "odds.csv"
  path = os.path.join(os.path.dirname(__file__), "..", "data","raw")
  filepath = os.path.join(path, filename)
  filepath = os.path.normpath(filepath)

  with open(filepath, "w+") as f:
    years = get_years(url)

if(__name__ == "__main__"):
  main()