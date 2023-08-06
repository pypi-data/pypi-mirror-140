# import Asclepius dependencies
from pandas.core.frame import DataFrame
from asclepius.instelling import GGZ, ZKH
from asclepius.medewerker import Medewerker
from asclepius.portaaldriver import PortaalDriver
from asclepius.testen import TestFuncties, Verklaren

# import other dependencies
from typing import Union
from pandas import ExcelWriter

class ReleaseTesten:
    
    def __init__(self, gebruiker: Medewerker, losse_bestanden: bool = False):

        # Initialiseren
        self.gebruiker = gebruiker
        self.portaaldriver = PortaalDriver(self.gebruiker)
        self.testfuncties = TestFuncties()
        self.verklaren = Verklaren()

        self.losse_bestanden = losse_bestanden
        
        return None

    def set_da_excels(self, *instellingen: ZKH, datum_zaterdag:str = None, datum_zondag:str = None):
        # Download excelbestanden
        mislukt = []
        for instelling in instellingen:
            try:
                instelling.excel_da_a = f'{self.gebruiker.bestemming}/{datum_zondag}/{instelling.klant_code}_da_a.xlsx'
                instelling.excel_da_a_test = f'{self.gebruiker.bestemming}/{datum_zondag}/{instelling.klant_code}_da_a_test.xlsx'

                instelling.excel_da_p = f'{self.gebruiker.bestemming}/{datum_zaterdag}/{instelling.klant_code}_da_p.xlsx'
                instelling.excel_da_p_test = f'{self.gebruiker.bestemming}/{datum_zaterdag}/{instelling.klant_code}_da_p_test.xlsx'
            except:
                mislukt.append(instelling.klant_code)

        # Print mislukte downloads/tests
        if len(mislukt) != 0:
            print('Mislukte koppelingen:', ' '.join(mislukt))
        else:
            print('Geen mislukte koppelingen!')
        return None
    
    def test_da(self, *instellingen: Union[GGZ, ZKH], download = True):

        # Download excelbestanden
        mislukt_download = []
        if download:
            for instelling in instellingen:
                try:
                    self.portaaldriver.webscraper_da(instelling)
                except:
                    mislukt_download.append(instelling.klant_code)
        else:
            pass

        # Test de DA
        mislukt_da = []
        for instelling in instellingen:
            try:        
                # Aantallencheck
                self.testfuncties.aantallencheck(instelling, False)
                self.testfuncties.aantallencheck(instelling, True)

                # Standaardverschillen vinden
                self.verklaren.standaardverschillen_da(instelling, False)
                self.verklaren.standaardverschillen_da(instelling, True)
            except:
                mislukt_da.append(instelling.klant_code)
        
        if self.losse_bestanden:
            for instelling in instellingen:
                if instelling.klant_code not in set(mislukt_download + mislukt_da):
                    with ExcelWriter(f'Bevindingen DA {instelling.klant_code}.xlsx') as writer:
                        instelling.bevindingen_da.to_excel(writer, sheet_name=f'{instelling.klant_code}')
                        instelling.bevindingen_da_test.to_excel(writer, sheet_name=f'{instelling.klant_code} test')
                else: pass
        else:
            with ExcelWriter(f'Bevindingen DA.xlsx') as writer:
                for instelling in instellingen:
                    if instelling.klant_code not in set(mislukt_download + mislukt_da):
                        instelling.bevindingen_da.to_excel(writer, sheet_name=f'{instelling.klant_code}')
                        instelling.bevindingen_da_test.to_excel(writer, sheet_name=f'{instelling.klant_code} test')
                    else: pass

        # Print mislukte downloads/tests
        if len(mislukt_download) != 0:
            print('Mislukte downloads:', ' '.join(mislukt_download))
        else:
            print('Geen mislukte downloads!')
        
        if len(mislukt_da) != 0:
            print('Mislukte DA tests:', ' '.join(mislukt_da))
        else:
            print('Geen mislukte DA tests!')
        return None
    
    def test_bi(self, *instellingen: Union[GGZ, ZKH]):
        # Download excelbestanden
        mislukt_download = []
        for instelling in instellingen:
            try:
                self.portaaldriver.webscraper_bi(instelling)
            except:
                mislukt_download.append(instelling.klant_code)

        # Test de BI
        mislukt_bi = []
        for instelling in instellingen:
            try:        
                # Vergelijk BI prestatiekaarten
                self.testfuncties.prestatiekaarten_vergelijken(instelling, 'bi')
            except:
                mislukt_bi.append(instelling.klant_code)

        if self.losse_bestanden:
            for instelling in instellingen:
                if instelling.klant_code not in set(mislukt_download + mislukt_bi):
                    with ExcelWriter(f'Bevindingen BI {instelling.klant_code}.xlsx') as writer:
                        instelling.bevindingen_bi.to_excel(writer, sheet_name=f'{instelling.klant_code}')
                else: pass
        else:
            with ExcelWriter(f'Bevindingen BI.xlsx') as writer:
                for instelling in instellingen:
                    if instelling.klant_code not in set(mislukt_download + mislukt_bi):
                        instelling.bevindingen_bi.to_excel(writer, sheet_name=f'{instelling.klant_code}')
                    else: pass
        
        # Print mislukte downloads/tests
        if len(mislukt_download) != 0:
            print('Mislukte downloads:', ' '.join(mislukt_download))
        else:
            print('Geen mislukte downloads!')

        if len(mislukt_bi) != 0:
            print('Mislukte BI tests:', ' '.join(mislukt_bi))
        else:
            print('Geen mislukte BI tests!')
        return None
    
    def test_zpm(self, *instellingen: Union[GGZ, ZKH]):
        # Download excelbestanden
        mislukt_download = []
        for instelling in instellingen:
            try:
                self.portaaldriver.webscraper_zpm(instelling)
            except:
                mislukt_download.append(instelling.klant_code)

        # Test de ZPM
        mislukt_zpm = []
        for instelling in instellingen:
            try:        
                # Vergelijk ZPM prestatiekaarten
                self.testfuncties.prestatiekaarten_vergelijken(instelling, 'zpm')
            except:
                mislukt_zpm.append(instelling.klant_code)

        if self.losse_bestanden:
            for instelling in instellingen:
                if instelling.klant_code not in set(mislukt_download + mislukt_zpm):
                    with ExcelWriter(f'Bevindingen ZPM {instelling.klant_code}.xlsx') as writer:
                        instelling.bevindingen_zpm.to_excel(writer, sheet_name=f'{instelling.klant_code}')
                else: pass
        else:
            with ExcelWriter(f'Bevindingen ZPM.xlsx') as writer:
                for instelling in instellingen:
                    if instelling.klant_code not in set(mislukt_download + mislukt_zpm):
                        instelling.bevindingen_zpm.to_excel(writer, sheet_name=f'{instelling.klant_code}')
                    else: pass

        # Print mislukte downloads/tests
        if len(mislukt_download) != 0:
            print('Mislukte downloads:', ' '.join(mislukt_download))
        else:
            print('Geen mislukte downloads!')
        
        if len(mislukt_zpm) != 0:
            print('Mislukte ZPM tests:', ' '.join(mislukt_zpm))
        else:
            print('Geen mislukte ZPM tests!')
        return None

    def test_zpm_nza(self, *instellingen: Union[GGZ, ZKH]):
        # Download excelbestanden
        mislukt_download = []
        for instelling in instellingen:
            try:
                self.portaaldriver.webscraper_zpm_nza(instelling)
            except:
                mislukt_download.append(instelling.klant_code)

        # Test de ZPM_NZA
        mislukt_zpm = []
        for instelling in instellingen:
            try:        
                # Vergelijk ZPM_NZA prestatiekaarten
                self.testfuncties.prestatiekaarten_vergelijken(instelling, 'zpm_nza')
            except:
                mislukt_zpm.append(instelling.klant_code)

        if self.losse_bestanden:
            for instelling in instellingen:
                if instelling.klant_code not in set(mislukt_download + mislukt_zpm):
                    with ExcelWriter(f'Bevindingen ZPM 100% NZA {instelling.klant_code}.xlsx') as writer:
                        instelling.bevindingen_zpm_nza.to_excel(writer, sheet_name=f'{instelling.klant_code}')
                else: pass
        else:
            with ExcelWriter(f'Bevindingen ZPM 100% NZA.xlsx') as writer:
                for instelling in instellingen:
                    if instelling.klant_code not in set(mislukt_download + mislukt_zpm):
                        instelling.bevindingen_zpm_nza.to_excel(writer, sheet_name=f'{instelling.klant_code}')
                    else: pass

        # Print mislukte downloads/tests
        if len(mislukt_download) != 0:
            print('Mislukte downloads:', ' '.join(mislukt_download))
        else:
            print('Geen mislukte downloads!')
        
        if len(mislukt_zpm) != 0:
            print('Mislukte ZPM 100% NZA tests:', ' '.join(mislukt_zpm))
        else:
            print('Geen mislukte ZPM 100% NZA tests!')
        return None

    def test_slm(self, *instellingen: Union[GGZ, ZKH]):
        # Download excelbestanden
        mislukt_download = []
        for instelling in instellingen:
            try:
                self.portaaldriver.webscraper_slm(instelling)
            except:
                mislukt_download.append(instelling.klant_code)

        # Test de BI
        bevindingen_slm = DataFrame({'Instelling': [], 'Delta totaal A': [], 'Delta totaal P': []})
        for instelling in instellingen:
            if instelling.klant_code not in set(mislukt_download):
                    new_row = {'Instelling': instelling.klant_code, 'Delta totaal A': instelling.slm_delta_a, 'Delta totaal P': instelling.slm_delta_p}
                    bevindingen_slm = bevindingen_slm.append(new_row, ignore_index = True)
            else: pass

        with ExcelWriter(f'Bevindingen SLM.xlsx') as writer:
            bevindingen_slm.to_excel(writer, sheet_name='SLM')
        
        # Print mislukte downloads/tests
        if len(mislukt_download) != 0:
            print('Mislukte downloads:', ' '.join(mislukt_download))
        else:
            print('Geen mislukte downloads!')
        return None

    
    def test_zpm_productie(self, *instellingen: Union[GGZ, ZKH]):
        # Download excelbestanden
        mislukt_download = []
        for instelling in instellingen:
            try:
                self.portaaldriver.webscraper_zpm_productie(instelling)
            except:
                mislukt_download.append(instelling.klant_code)

        # Test de ZPM_NZA
        mislukt_zpm = []
        for instelling in instellingen:
            try:        
                # Vergelijk ZPM_NZA prestatiekaarten
                self.testfuncties.prestatiekaarten_vergelijken(instelling, 'zpm_productie')
            except:
                mislukt_zpm.append(instelling.klant_code)

        if self.losse_bestanden:
            for instelling in instellingen:
                if instelling.klant_code not in set(mislukt_download + mislukt_zpm):
                    with ExcelWriter(f'Bevindingen ZPM Productie {instelling.klant_code}.xlsx') as writer:
                        instelling.bevindingen_zpm_productie.to_excel(writer, sheet_name=f'{instelling.klant_code}')
                else: pass
        else:
            with ExcelWriter(f'Bevindingen ZPM Productie.xlsx') as writer:
                for instelling in instellingen:
                    if instelling.klant_code not in set(mislukt_download + mislukt_zpm):
                        instelling.bevindingen_zpm_productie.to_excel(writer, sheet_name=f'{instelling.klant_code}')
                    else: pass

        # Print mislukte downloads/tests
        if len(mislukt_download) != 0:
            print('Mislukte downloads:', ' '.join(mislukt_download))
        else:
            print('Geen mislukte downloads!')
        
        if len(mislukt_zpm) != 0:
            print('Mislukte ZPM Productie tests:', ' '.join(mislukt_zpm))
        else:
            print('Geen mislukte ZPM Productie tests!')
        return None
    
