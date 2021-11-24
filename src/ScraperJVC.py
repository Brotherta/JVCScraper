from src import *


JVC_URL = "https://www.jeuxvideo.com/jeux/"
GOOGLE_URL = "https://www.google.com/search?channel=crow5&client=firefox-b-d&q=jeuxvideo.com+"
FILEPATH_SCRAP = "scraps/all_avis.csv"

class ScraperJVC(object):
    games_list: list
    index_all: int
    index_choose_another_game: int
    index_quit: int
    choices: str
    data: pd.DataFrame
    status: int

    def __init__(self) -> None:
        self.games_list = []
        self.index_all = 0
        self.index_choose_another_game = 0
        self.index_quit = 0
        self.choices = ""
        self._init_data()
        self.status = 1


    def _init_data(self):
        try:
            self.data = pd.read_csv(FILEPATH_SCRAP, na_values=('NaN', 'NA', ''), index_col=0)
        except FileNotFoundError as e:
            self.data = pd.DataFrame(data={'jeux': [], 'note': [], 'avis': []})


    def _init_choices(self):
        self.choices = "Games found"
        for i in range(self.index_choose_another_game-1):
            game: GameJVC = self.games_list[i]
            self.choices += f'\n - ({i}) (nb_avis {game.nb_avis}) {game.title_article}'
        self.choices += f'\n - ({self.index_all}) scrapes all games.'
        self.choices += f'\n - ({self.index_choose_another_game}) choose an other game.'
        self.choices += f'\n - ({self.index_quit}) quit scrapers'


    def _get_blocs_avis(self, soup : BeautifulSoup):
        bloc_avis_tous = soup.find('div', class_='bloc-avis-tous')
        return bloc_avis_tous.find_all('div', class_='bloc-avis')


    def _scrape_google(self, query):
        query = urllib.parse.quote_plus(query)
        response = self._get_source("https://www.google.co.uk/search?q=" + query)

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


    def _get_source(self, url):
        try:
            session = HTMLSession()
            response = session.get(url)
            return response

        except requests.exceptions.RequestException as e:
            print(e)


    def start_search(self):
        game_name = ""
        self.games_list.clear()

        while game_name == "":
            game_name = input("Search for a game : (ex: World of Warcraft) (Type quit to exit the programs) \n")
            
            if game_name == "quit":
                exit(0)

            links = self._scrape_google('jeuxvideo.com ' + game_name + ' avis')

            links_game = []
            for link in links:
                link: str
                if link.startswith(JVC_URL) and 'avis' in link:
                    links_game.append(link)

            if len(links_game) == 0:
                print("The game searched does not exist. Please retry.")
                game_name = ""
        
        index = 0
        for link in links_game:
            req = requests.get(link).text
            soup = BeautifulSoup(req, 'html.parser')

            game = GameJVC()
            game.id = index
            game.url = link
            game.game_name = game_name
            game.title_article = soup.find('title').text
            game.nb_avis = soup.find('div', class_='nb-total-avis').text
            self.games_list.append(game)

            index+=1
        
        self.index_all = index
        self.index_choose_another_game = index + 1
        self.index_quit =  index + 2


    def start_choices(self):
        choice = -1
        self._init_choices()

        while choice == -1:
            print(self.choices)
            choice = int(input("Choose a game : (ex: 0)\n"))
            if choice < 0 or choice > self.index_quit:
                choice = -1
                print(f"Wrong choice, please type a correct number. Type {self.index_quit} to quit.")
        
            if choice == self.index_quit:
                exit(0)
            elif choice == self.index_choose_another_game:
                choice = -1
                self.start_search()
                self._init_choices()
            elif choice == self.index_all:
                pass
            else:
                game = self.games_list[choice]
                self.games_list.clear()
                self.games_list.append(game)
    

    def start_scraps(self):
        game: GameJVC
        for game in self.games_list:
            html = requests.get(game.url).text
            soup = BeautifulSoup(html, 'html.parser')

            pages = soup.find_all('a', class_='lien-jv')

            nb_pages = 1
            if len(pages) != 0:
                nb_pages = int(pages[len(pages)-1].text)
            
            print("Scrapping ", game.nb_avis, " from ", game.url)
            for i in trange(1,nb_pages+1):
                html = requests.get(f'{game.url}?p={i}').text
                soup = BeautifulSoup(html, 'html.parser') 

                blocs = self._get_blocs_avis(soup)

                bloc: BeautifulSoup
                for bloc in blocs:
                    try:
                        note = bloc.find('div', class_='note-avis').find('strong').text
                        avis = bloc.find('p').text
                        new_row = {'jeux': game.game_name, 'note': note, 'avis': avis}
                        self.data = self.data.append(new_row, ignore_index=True)
                    except:
                        # corrupted avis
                        pass
            

    def save_data(self):
        self.data.to_csv(FILEPATH_SCRAP)
        print(f'results are saved game in {FILEPATH_SCRAP}')




