import requests
from bs4 import BeautifulSoup
from tqdm import trange
import urllib
import pandas as pd
from requests_html import HTMLSession

JVC_URL = "https://www.jeuxvideo.com/jeux/"
GOOGLE_URL = "https://www.google.com/search?channel=crow5&client=firefox-b-d&q=jeuxvideo.com+"


class ScraperJVC(object):

    def __init__(self) -> None:
        pass


    def scrape_google(self, query):
        query = urllib.parse.quote_plus(query)
        response = self.get_source("https://www.google.co.uk/search?q=" + query)

        links = list(response.html.absolute_links)
        google_domains = ('https://www.google.', 
                        'https://google.', 
                        'https://webcache.googleusercontent.', 
                        'http://webcache.googleusercontent.', 
                        'https://policies.google.',
                        'https://support.google.',
                        'https://maps.google.')

        for url in links[:]:
            if url.startswith(google_domains):
                links.remove(url)

        return links


    def get_source(self, url):
        try:
            session = HTMLSession()
            response = session.get(url)
            return response

        except requests.exceptions.RequestException as e:
            print(e)

    
    def start_search(self):
        game_name = ""
        while game_name == "":
            game_name = input("Search for a game : (ex: World of Warcraft)\n")
            links = self.scrape_google('jeuxvideo.com ' + game_name + ' avis')

            links_game = []
            for link in links:
                link: str
                if link.startswith(JVC_URL) and 'avis' in link:
                    links_game.append(link)

            if len(links_game) == 0:
                print("The game searched does not exist. Please retry.")
                game_name = ""


