# import Asclepius dependencies
from asclepius.instelling import GGZ, ZKH

# import other dependencies
import getpass
import os
import time
from typing import Union
import shutil

class Medewerker:
    
    def __init__(self, gebruikersnaam, downloads, bestemming):
        self.gebruikersnaam = gebruikersnaam
        self.wachtwoord = getpass.getpass(prompt='Wachtwoord: ')
        self.downloads = downloads
        self.bestemming = bestemming

    def laatste_download(self):
        # kijk welke bestanden er in downloads staan
        files = os.listdir(self.downloads)

        # converteer de gevonden namen naar paths
        paths = [os.path.join(self.downloads, basename) for basename in files]

        # vind het nieuwste bestand
        last_created_file = (max(paths, key = os.path.getctime))

        # vind de tijd waarop het nieuwste bestand is aangemaakt
        last = time.gmtime(os.path.getmtime(last_created_file))
        
        return last_created_file, last
    
    def genereer_nieuwe_map(self):
        today = time.gmtime()
        new_folder = f'{today.tm_year}-{today.tm_mon}-{today.tm_mday}'
        new_path = os.path.join(self.bestemming, new_folder)

        if not os.path.exists(new_path):
            os.makedirs(new_path)
        return new_path

    def webscraper_hernoem_bestand(self, instelling: Union[GGZ, ZKH], product: str, test: bool = False):
        last_created_file, last = self.laatste_download()

        today = time.gmtime()
        if last.tm_mday == today.tm_mday and last.tm_mon == today.tm_mon:
            # nieuwe bestandsnaam en nieuwe map
            new_name = instelling.genereer_nieuwe_naam(product, test)
            new_folder = self.genereer_nieuwe_map()
            new_path = os.path.join(new_folder, new_name)

            shutil.move(last_created_file, new_path)
            instelling.update_bestand_locatie(product, new_path, test)
        else:
            print("Bestand niet gevonden/hernoemen mislukt")
        return None
