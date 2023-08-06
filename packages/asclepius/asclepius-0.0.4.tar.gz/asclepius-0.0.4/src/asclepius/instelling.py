# import hardcoded information from fileserver
import sys
sys.path.append(r'\\fileserver.valuecare.local\Algemeen\Automatisch testen\Python')
from parameters import HardCodedParameters

# import other dependencies
from pandas import DataFrame

class Instelling:
    def __init__(self, klant_code: str):
        self.klant_code = klant_code
        self.baselink = ''
        self.huidige_omgeving = ''
        self.link_dict = {}

        # Daily Audit
        self.tolerantie_abs = 0
        self.tolerantie_pct = 0
        self.excel_da_a = 'excel_da_a file'
        self.excel_da_p = 'excel_da_p file'
        self.bevindingen_da = DataFrame()

        self.excel_da_a_test = 'excel_da_test_a file'
        self.excel_da_p_test = 'excel_da_test_p file'
        self.bevindingen_da_test = DataFrame()

        # BI prestatiekaart
        self.excel_bi_a = 'excel_bi_a file'
        self.excel_bi_p = 'excel_bi_p file'
        self.bevindingen_bi = DataFrame()

        # ZPM prestatiekaart
        self.excel_zpm_a = 'excel_zpm_a file'
        self.excel_zpm_p = 'excel_zpm_p file'
        self.bevindingen_zpm = DataFrame()

        # ZPM_NZA prestatiekaart
        self.excel_zpm_nza_a = 'excel_zpm_nza_a file'
        self.excel_zpm_nza_p = 'excel_zpm_nza_p file'
        self.bevindingen_zpm_nza = DataFrame()

        # ZPM_Productie prestatiekaart
        self.excel_zpm_productie_a = 'excel_zpm_productie_a file'
        self.excel_zpm_productie_p = 'excel_zpm_productie_p file'
        self.bevindingen_zpm_productie = DataFrame()

        # SLM deltas totaal
        self.slm_delta_a = ''
        self.slm_delta_p = ''
        return None
    
    def update_baselink(self):
        # login link
        self.login = self.baselink + self.link_dict['login']
        
        # DA links
        self.daily_audit = self.baselink + self.link_dict['daily_audit']
        self.da_excel_download = self.daily_audit + self.link_dict['da_excel_download']
        self.daily_audit_test = self.baselink + self.link_dict['daily_audit_test']
        self.da_test_excel_download = self.daily_audit_test + self.link_dict['da_test_excel_download']
        self.da_excel_groot_download = self.daily_audit + self.link_dict['da_excel_groot_download']

        # BI links
        self.bi_prestatiekaart = self.baselink + self.link_dict['bi_prestatiekaart']
        self.bi_excel_download = self.baselink + self.link_dict['bi_excel_download']

        # zpm links
        self.zpm_prestatiekaart = self.baselink + self.link_dict['zpm_prestatiekaart']
        self.zpm_excel_download = self.baselink + self.link_dict['zpm_excel_download']

        # zpm_nza links
        self.zpm_nza_prestatiekaart = self.baselink + self.link_dict['zpm_nza_prestatiekaart']
        self.zpm_nza_excel_download = self.baselink + self.link_dict['zpm_nza_excel_download']

        # zpm_nza links
        self.zpm_productie_prestatiekaart = self.baselink + self.link_dict['zpm_productie_prestatiekaart']
        self.zpm_productie_excel_download = self.baselink + self.link_dict['zpm_productie_excel_download']

        # slm links
        self.slm_per_verzekeraar = self.baselink + self.link_dict['slm_per_verzekeraar']

        return None

    def kies_omgeving(self, omgeving: str):
        if omgeving == 'acceptatie':
            # verander huidige omgeving naar acceptatie
            self.huidige_omgeving = 'acceptatie'
        elif omgeving == 'productie':
            # verander huidige omgeving naar productie
            self.huidige_omgeving = 'productie'
        else:
            pass
        
        self.baselink = HardCodedParameters.baselink + self.huidige_omgeving[0] + self.klant_code + '/portaal/'
        self.update_baselink()
        return None
    
    def genereer_nieuwe_naam(self, product: str, test: bool = False):
        if test:
            new_name = f'{self.klant_code}_{product}_{self.huidige_omgeving[0]}_test.xlsx'
        else:
            new_name = f'{self.klant_code}_{product}_{self.huidige_omgeving[0]}.xlsx'
        return new_name
    
    def update_bestand_locatie(self, product, new_path, test):
        if test:
            attr = f'excel_{product}_{self.huidige_omgeving[0]}_test'
        else:
            attr = f'excel_{product}_{self.huidige_omgeving[0]}'
        
        setattr(self, attr, new_path)
        return None
    
    def set_slm_delta(self, rode_delta: str):
        attr = f'slm_delta_{self.huidige_omgeving[0]}'
        setattr(self, attr, rode_delta)
        return None


class ZKH(Instelling):

    def __init__(self, klant_code: str):
        super().__init__(klant_code)

        self.da = True
        self.tolerantie_abs = 0 # 7
        self.tolerantie_pct = 0 # 2

        self.link_dict = HardCodedParameters.zkh_dict

        self.update_baselink()
        return None


class GGZ(Instelling):

    variabele_links = HardCodedParameters.ggz_variabele_links

    def __init__(self, klant_code: str):
        super().__init__(klant_code)

        self.link_dict = HardCodedParameters.ggz_dict

        self.update_link_dict()

        self.update_baselink()
        return None
    
    def update_link_dict(self):
        if self.klant_code in GGZ.variabele_links.index.tolist():
            self.link_dict['bi_prestatiekaart'] = GGZ.variabele_links['bi_prestatiekaart'][self.klant_code]
            self.link_dict['bi_excel_download'] = GGZ.variabele_links['bi_excel_download'][self.klant_code]
        else:
            pass
        return None