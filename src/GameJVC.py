from src import *


class GameJVC(object):
    game_name: str
    url: str
    id: int
    nb_avis: int
    title_article: str
    

    def __init__(self) -> None:
        self.game_name = ""
        self.url = ""
        self.id = -1
        self.nb_avis = 0
        self.title_article = ""
