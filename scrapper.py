import requests
from bs4 import BeautifulSoup
import json
from tqdm import trange
import urllib
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession

DEBUG = True
FILEPATH_SCRAP = "scraps/all_avis.csv"
JVC_URL = "https://www.jeuxvideo.com/jeux/"
GOOGLE_URL = "https://www.google.com/search?channel=crow5&client=firefox-b-d&q=jeuxvideo.com+"

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


def get_blocs_avis(soup : BeautifulSoup):
    bloc_avis_tous = soup.find('div', class_='bloc-avis-tous')
    return bloc_avis_tous.find_all('div', class_='bloc-avis')





if __name__ == "__main__":
    game = ""
    html =""
    soup: BeautifulSoup


    if not DEBUG:
    
        while game == "":
            game = input("Search for a game : (ex: World of Warcraft)\n")
            links = scrape_google('jeuxvideo.com ' + game + ' avis')

            links_game = []
            for link in links:
                link: str
                if link.startswith(JVC_URL) and 'avis' in link:
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

    else:
        url = "https://www.jeuxvideo.com/jeux/pc/jeu-11212/avis/"
        game = "test"

    
    print("url : ", url)
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')

    pages = soup.find_all('a', class_='lien-jv')

    nb_pages = 1
    if len(pages) != 0:
        nb_pages = int(pages[len(pages)-1].text)
    
    
    data: pd.DataFrame
    try:
        data = pd.read_csv("scraps/all_avis.csv", na_values=('NaN', 'NA', ''), index_col=0)
    except FileNotFoundError as e:
        data = pd.DataFrame(data={'jeux': [], 'note': [], 'avis': []})
    
    
    for i in trange(1,nb_pages+1):
        html = requests.get(f'{url}?p={i}').text
        soup = BeautifulSoup(html, 'html.parser') 

        blocs = get_blocs_avis(soup)

        bloc: BeautifulSoup
        for bloc in blocs:
            note = bloc.find('div', class_='note-avis').find('strong').text
            avis = bloc.find('p').text
            avis = avis
            new_row = {'jeux': game, 'note': note, 'avis': avis}
            data = data.append(new_row, ignore_index=True)
            
            
    nb_avis = len(data)
    print(nb_avis, "advices has been scrapped.")

    filename = FILEPATH_SCRAP

    data.to_csv(FILEPATH_SCRAP)
    print(f'results are saved game in {filename}')


        
    

    