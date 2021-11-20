import requests
from bs4 import BeautifulSoup
import json
import sys
from tqdm import trange

proxyhttp = "http://68.188.59.198:80"

proxy = {
    "https" : proxyhttp
}

def get_blocs(soup : BeautifulSoup):
    blocs = []
    all = soup.find_all('div', class_='bloc-avis-tous')

    for bloc in all:
        blocs.append(bloc.find('div', class_='bloc-avis'))    

    return blocs


def main():

    for i in range(1,301):
        url = f'https://www.jeuxvideo.com/jeux/pc/jeu-38024/avis/?p={i}'
        print("\n\n\n\n\n\n\n\n\n\n\nrequete numéro :", i)
        print(requests.get(url).text)
        


if __name__ == "__main__":
    args = sys.argv[1:]
    
    if len(args) != 2:
        print("Usage: [game name] [jvc url avis]")
        exit(1)
    
    game = args[0]
    url = args[1]

    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')  

    pages = soup.find_all('a', class_='lien-jv')
    
    if (len(pages) <= 0):
        print("Url is not correct, ensure to give url from avis. ex: https://www.jeuxvideo.com/jeux/pc/jeu-XXXX/avis/")
        exit(1)

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
       
            data.append({note : avis})

    print(json.dumps(data, indent=4, ensure_ascii=False))
        
    

    