import requests
from bs4 import BeautifulSoup
import json
from tqdm import trange
import urllib
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession
import re

proxyhttp = "http://68.188.59.198:80"

proxy = {
    "https" : proxyhttp
}

def scrape_google(query):

    query = urllib.parse.quote_plus(query)
    response = get_source("https://www.google.co.uk/search?q=" + query)

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


def get_source(url):

    try:
        session = HTMLSession()
        response = session.get(url)
        return response

    except requests.exceptions.RequestException as e:
        print(e)


def get_blocs(soup : BeautifulSoup):
    blocs = []
    all = soup.find_all('div', class_='bloc-avis-tous')

    for bloc in all:
        blocs.append(bloc.find('div', class_='bloc-avis'))    

    print("\n\nDEBUG bloc len :", len(blocs))
    return blocs

        

if __name__ == "__main__":
    game = ""
    URL = "https://www.google.com/search?channel=crow5&client=firefox-b-d&q=jeuxvideo.com+"

    html =""
    soup: BeautifulSoup

    while game == "":
        game = input("Search for a game : (ex: World of Warcraft)\n")
        links = scrape_google('jeuxvideo.com ' + game + ' avis')

        links_game = []
        for link in links:
            link: str
            if link.startswith('https://www.jeuxvideo.com/jeux/') and 'avis' in link:
                links_game.append(link)

        if len(links_game) == 0:
            print("The game searched does not exist. Please retry.")
            game = ""
    
    games_dict = {}
    games_dict_index = {}
    index = 0
    for link in links_game:
        req = requests.get(link).text
        soup = BeautifulSoup(req, 'html.parser')
        title = soup.find('title').text
        games_dict[title] = link
        games_dict_index[index] = title
        index+=1


    choices = "Games availables"
    for i in range(index-1):
        choices += f'\n - ({i}) {games_dict_index[i]}'

    choice = -2
    while choice == -2:
        print(choices)
        print("\n")
        choice = int(input("Choose a game : (ex: 0) enter -1 for scrappes all\n"))
    
    url = games_dict[games_dict_index[choice]]
    print(url)
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')

    pages = soup.find_all('a', class_='lien-jv')

    nb_pages = int(pages[len(pages)-1].text)
    
    blocs = get_blocs(soup);

    data = []

    for i in trange(1,nb_pages):
        html = requests.get(f'{url}?p={i}').text
        soup = BeautifulSoup(html, 'html.parser') 

        bloc: BeautifulSoup
        for bloc in blocs:
            note = bloc.find('div', class_='note-avis').find('strong').text
            avis = bloc.find('p').text
            print("note : ", note)
            print("avis : ", avis)
            data.append({note : avis})
    
    with open(f'scraps/{game}.json', 'w') as f:
        json.dumps(data, indent=4, ensure_ascii=False)

    print(f'{game}.json created in scraps folder.')
        
    

    