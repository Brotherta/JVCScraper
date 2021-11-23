import requests
from bs4 import BeautifulSoup
from tqdm import trange
import urllib
import pandas as pd
from requests_html import HTMLSession


class GameJVC(object):
    game_name: str
    url: str
    id: int
    nb_avis: int
    title_article: str
    

    def __init__(self) -> None:
        self.game = ""
        self.url = ""
        self.id = -1
        self.nb_avis = 0
        self.title_article = ""

    