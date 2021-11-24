from src import *

if __name__ == "__main__":
    scraps = ScraperJVC()
    while(scraps.status != 0):
        scraps.start_search()
        scraps.start_choices()
        scraps.start_scraps()
        scraps.save_data()