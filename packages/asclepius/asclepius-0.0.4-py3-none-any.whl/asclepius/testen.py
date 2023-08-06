# import Asclepius dependencies
from asclepius.instelling import GGZ, ZKH, HardCodedParameters

# import other dependencies
from pandas import read_excel, merge, isnull, DataFrame
from typing import Union

class TestFuncties:

    def __init__(self):
        pass

        # DAILY AUDIT FUNCTIES

    def wrangle_da(self, excel_a, excel_p) -> DataFrame:
        # import excelsheets
        data_a = read_excel(excel_a, index_col = None, header = 2)
        data_p = read_excel(excel_p, index_col = None, header = 2)

        if data_a.columns.values[0] == 'Controle/norm':
            # rename columns
            data_a = data_a.rename(columns = {'Controle/norm': 'controle', 'Aantal': 'aantal_a', 'Impact': 'impact_a'})
            data_p = data_p.rename(columns = {'Controle/norm': 'controle', 'Aantal': 'aantal_p', 'Impact': 'impact_p'})
        else:
            # rename columns
            data_a = data_a.rename(columns = {'Controle': 'controle', 'Aantal': 'aantal_a', 'Impact': 'impact_a'})
            data_p = data_p.rename(columns = {'Controle': 'controle', 'Aantal': 'aantal_p', 'Impact': 'impact_p'})
            
        # Outer join van de dataframes op controle
        wrangled_data = merge(data_a, data_p, how = 'outer', on = 'controle')

        # drop impact_a and impact_p
        wrangled_data = wrangled_data.drop(columns=['impact_a', 'impact_p'])

        # fill NaN values
        wrangled_data['aantal_a'] = wrangled_data['aantal_a'].fillna(0)

        # add absolute and percentual difference
        wrangled_data = wrangled_data.assign(diff_abs = wrangled_data['aantal_a'] - wrangled_data['aantal_p'])
        wrangled_data = wrangled_data.assign(diff_pct = round((wrangled_data['diff_abs'] / wrangled_data['aantal_p']) * 100, 2))

        # if P is NaN
        wrangled_data['aantal_p'] = wrangled_data['aantal_p'].fillna(0)
        wrangled_data['diff_abs'] = wrangled_data['diff_abs'].fillna(wrangled_data['aantal_a'])
        wrangled_data['diff_pct'] = wrangled_data['diff_pct'].fillna(100.00)

        return wrangled_data

    def check_verschillen_da(self, wrangled_data: DataFrame, tolerantie_abs: int, tolerantie_pct: int):
        verschillen = DataFrame(columns = list(wrangled_data.columns.values))
        for i in range(len(wrangled_data)):
            entry = wrangled_data.iloc[i, :]
            if abs(entry['diff_abs']) > tolerantie_abs and abs(entry['diff_pct']) > tolerantie_pct:
                verschillen = verschillen.append(entry)
        return verschillen

    def aantallencheck(self, instelling: Union[GGZ, ZKH], test: bool = False):
        if test:
            excel_a = instelling.excel_da_a_test
            excel_p = instelling.excel_da_p_test
        else:
            excel_a = instelling.excel_da_a
            excel_p = instelling.excel_da_p
        
        actieaantallen = self.wrangle_da(excel_a, excel_p)
        bevindingen = self.check_verschillen_da(actieaantallen, instelling.tolerantie_abs, instelling.tolerantie_pct)
        if len(bevindingen) == 0:
            print('Geen significante verschillen gevonden')
        else:
            pass

        if test:
            instelling.bevindingen_da_test = bevindingen
        else:
            instelling.bevindingen_da = bevindingen
        return None

    # PRESTATIEKAART FUNCTIES

    def wrangle_pk(self, excel_a, excel_p):
        # import excelsheets
        data_a = read_excel(excel_a, index_col = None, header = 0)
        data_p = read_excel(excel_p, index_col = None, header = 0)

        # drop Verschil column
        data_a = data_a.drop(columns=['Verschil'])
        data_p = data_p.drop(columns=['Verschil'])

        # voeg index column toe
        data_a['index_a'] = data_a.index
        data_p['index_p'] = data_p.index

        # hernoem kolommen
        data_a = data_a.rename(columns = {'Titel': 'titel', 'Norm': 'norm_a', 'Realisatie': 'real_a', 'sectie': 'sectie_a'})
        data_p = data_p.rename(columns = {'Titel': 'titel', 'Norm': 'norm_p', 'Realisatie': 'real_p', 'sectie': 'sectie_p'})

        # join dataframes op titlel
        wrangled_data = merge(data_a, data_p, how = 'outer', on = 'titel')

        # return de prestatiekaart data
        return wrangled_data

    def check_existence(self, prestatiekaart, bevindingen):
        # checkt of een titel niet in A bestaat, niet in P bestaat
        for i in range(len(prestatiekaart)):
            if isnull(prestatiekaart['index_a'][i]):
                new_row = {'Indicator': prestatiekaart['titel'][i], 'Norm/Realisatie': 'Beiden', 'A': '', 'P': '', 'Bevinding': "Indicator niet in A portaal."}
                bevindingen = bevindingen.append(new_row, ignore_index = True)
                prestatiekaart = prestatiekaart.drop(index = i)
            elif isnull(prestatiekaart['index_p'][i]):
                new_row = {'Indicator': prestatiekaart['titel'][i], 'Norm/Realisatie': 'Beiden', 'A': '', 'P': '', 'Bevinding': "Indicator niet in P portaal."}
                bevindingen = bevindingen.append(new_row, ignore_index = True)
                prestatiekaart = prestatiekaart.drop(index = i)
            else:
                pass
        prestatiekaart = prestatiekaart.reset_index(drop = True)
        
        return prestatiekaart, bevindingen

    def check_empty(self, prestatiekaart, bevindingen):
        # checkt of een titel niet leeg is in A en P
        for i in range(len(prestatiekaart)):
            if isnull(prestatiekaart['norm_a'][i]) and isnull(prestatiekaart['real_a'][i]) and isnull(prestatiekaart['norm_p'][i]) and isnull(prestatiekaart['real_p'][i]):
                new_row = {'Indicator': prestatiekaart['titel'][i], 'Norm/Realisatie': 'Beiden', 'A': '', 'P': '', 'Bevinding': "Indicator is leeg in beide portalen."}
                bevindingen = bevindingen.append(new_row, ignore_index = True)
                prestatiekaart = prestatiekaart.drop(index = i)
            elif isnull(prestatiekaart['norm_a'][i]) and isnull(prestatiekaart['real_a'][i]):
                new_row = {'Indicator': prestatiekaart['titel'][i], 'Norm/Realisatie': 'Beiden', 'A': '', 'P': '', 'Bevinding': "Indicator is leeg in A portaal."}
                bevindingen = bevindingen.append(new_row, ignore_index = True)
                prestatiekaart = prestatiekaart.drop(index = i)
            elif isnull(prestatiekaart['norm_p'][i]) and isnull(prestatiekaart['real_p'][i]):
                new_row = {'Indicator': prestatiekaart['titel'][i], 'Norm/Realisatie': 'Beiden', 'A': '', 'P': '', 'Bevinding': "Indicator is leeg in P portaal."}
                bevindingen = bevindingen.append(new_row, ignore_index = True)
                prestatiekaart = prestatiekaart.drop(index = i)
            else:
                pass
        prestatiekaart = prestatiekaart.reset_index(drop = True)
        
        return prestatiekaart, bevindingen

    def check_normen(self, prestatiekaart, bevindingen):
        for i in range(len(prestatiekaart)):
            # Als beide normen leeg zijn zal daar waarschijnlijk een goede reden voor zijn
            if isnull(prestatiekaart['norm_a'][i]) and isnull(prestatiekaart['norm_p'][i]):
                pass
            # check of de norm niet leeg is in het A portaal
            elif isnull(prestatiekaart['norm_a'][i]):
                new_row = {'Indicator': prestatiekaart['titel'][i], 'Norm/Realisatie': 'Norm', 'A': '', 'P': '', 'Bevinding': "Norm leeg in A portaal."}
                bevindingen = bevindingen.append(new_row, ignore_index = True)
            # check of de norm niet leeg is in het P portaal
            elif isnull(prestatiekaart['norm_p'][i]):
                new_row = {'Indicator': prestatiekaart['titel'][i], 'Norm/Realisatie': 'Norm', 'A': '', 'P': '', 'Bevinding': "Norm leeg in P portaal."}
                bevindingen = bevindingen.append(new_row, ignore_index = True)
            # check of de normen in het A en het P portaal gelijk zijn aan elkaar
            elif not (prestatiekaart['norm_a'][i] == prestatiekaart['norm_p'][i]):
                new_row = {'Indicator': prestatiekaart['titel'][i], 'Norm/Realisatie': 'Norm', 'A': str(prestatiekaart['norm_a'][i]), 'P': str(prestatiekaart['norm_p'][i]), 'Bevinding': 'Norm in A wijkt af van P.'}
                bevindingen = bevindingen.append(new_row, ignore_index = True)
            else:
                pass
        
        # geef de prestatiekaart en bevindingen als output
        return prestatiekaart, bevindingen

    def check_realisaties(self, prestatiekaart, bevindingen):
        for i in range(len(prestatiekaart)):
            if isnull(prestatiekaart['real_a'][i]) or isnull(prestatiekaart['real_p'][i]):
                if isnull(prestatiekaart['real_a'][i]) and isnull(prestatiekaart['real_p'][i]):
                    new_row = {'Indicator': prestatiekaart['titel'][i], 'Norm/Realisatie': 'Realisatie', 'A': '', 'P': '', 'Bevinding': "Realisatie leeg in A en P portaal."}
                    bevindingen = bevindingen.append(new_row, ignore_index = True)
                else:
                    if isnull(prestatiekaart['real_a'][i]):
                        new_row = {'Indicator': prestatiekaart['titel'][i], 'Norm/Realisatie': 'Realisatie', 'A': '', 'P': '', 'Bevinding': "Realisatie leeg in A portaal."}
                        bevindingen = bevindingen.append(new_row, ignore_index = True)
                    else:
                        pass
                    if isnull(prestatiekaart['real_p'][i]):
                        new_row = {'Indicator': prestatiekaart['titel'][i], 'Norm/Realisatie': 'Realisatie', 'A': '', 'P': '', 'Bevinding': "Realisatie leeg in P portaal."}
                        bevindingen = bevindingen.append(new_row, ignore_index = True)
                    else:
                        pass
            elif not (prestatiekaart['real_a'][i] == prestatiekaart['real_p'][i]):
                new_row = {'Indicator': prestatiekaart['titel'][i], 'Norm/Realisatie': 'Realisatie', 'A': str(prestatiekaart['real_a'][i]), 'P': str(prestatiekaart['real_p'][i]), 'Bevinding': 'Realisatie in A wijkt af van P.'}
                bevindingen = bevindingen.append(new_row, ignore_index = True)
            else:
                pass
            
        return prestatiekaart, bevindingen

    def aantal_indicatoren(self, wrangled_data: DataFrame):
        lengte_a = wrangled_data['index_a'].max() + 1
        lengte_p = wrangled_data['index_p'].max() + 1
        return lengte_a, lengte_p

    def conclusie(self, bevindingen, lengte_a: int, lengte_p: int):
        lengte_bevingingen = len(bevindingen)
        new_row = {'Indicator': 'Aantal indicatoren in Prestatiekaart:', 'Norm/Realisatie': '', 'A': str(lengte_a), 'P': str(lengte_p), 'Bevinding': ''}
        bevindingen = bevindingen.append(new_row, ignore_index = True)
        new_row = {'Indicator': 'Totaal aantal bevindingen:', 'Norm/Realisatie': '', 'A': '', 'P': '', 'Bevinding': lengte_bevingingen}
        bevindingen = bevindingen.append(new_row, ignore_index = True)
        return bevindingen
    
    def prestatiekaarten_vergelijken(self, instelling: Union[GGZ, ZKH], product: str):
        if product == 'bi':
            excel_a = instelling.excel_bi_a
            excel_p = instelling.excel_bi_p
        elif product == 'zpm':
            excel_a = instelling.excel_zpm_a
            excel_p = instelling.excel_zpm_p
        elif product == 'zpm_nza':
            excel_a = instelling.excel_zpm_nza_a
            excel_p = instelling.excel_zpm_nza_p
        elif product == 'zpm_productie':
            excel_a = instelling.excel_zpm_productie_a
            excel_p = instelling.excel_zpm_productie_p
        else:
            print('Geen valide prestatiekaart om te vergelijken!')
            pass

        prestatiekaart = self.wrangle_pk(excel_a, excel_p)
        bevindingen = DataFrame({'Indicator': [], 'Norm/Realisatie': [], 'A': [], 'P': [], 'Bevinding': []})

        lengte_a, lengte_p = self.aantal_indicatoren(prestatiekaart)
        
        prestatiekaart, bevindingen = self.check_existence(prestatiekaart, bevindingen)
        
        prestatiekaart, bevindingen = self.check_empty(prestatiekaart, bevindingen)
        
        prestatiekaart, bevindingen = self.check_normen(prestatiekaart, bevindingen)
        
        prestatiekaart, bevindingen = self.check_realisaties(prestatiekaart, bevindingen)

        bevindingen = self.conclusie(bevindingen, lengte_a, lengte_p)
        
        if product == 'bi':
            instelling.bevindingen_bi = bevindingen
        elif product == 'zpm':
            instelling.bevindingen_zpm = bevindingen
        elif product == 'zpm_nza':
            instelling.bevindingen_zpm_nza = bevindingen
        elif product == 'zpm_productie':
            instelling.bevindingen_zpm_productie = bevindingen
        else:
            pass
        return None



class Verklaren:

    def __init__(self) :
        pass

    def splits_controle_omschrijving(self, bevindingen: DataFrame) -> DataFrame:
        gesplitste_controle = bevindingen["controle"].str.split(pat=" - ", n=1, expand = True)
        #bevindingen = bevindingen.assign(kenmerk = gesplitste_controle[0], omschrijving = gesplitste_controle[1])
        bevindingen['kenmerk'] = gesplitste_controle[0].to_list()
        bevindingen['omschrijving'] = gesplitste_controle[1].to_list()
        bevindingen = bevindingen[['kenmerk', 'omschrijving', 'aantal_a', 'aantal_p', 'diff_abs', 'diff_pct']]
        return bevindingen

    def standaardverschillen_da(self, instelling: Union[GGZ, ZKH], test: bool = False):
        # Check of de instelling in het standaardverschillen dict voorkomt
        if instelling.klant_code in HardCodedParameters.standaardverschillen_da:
            if test:
                bevindingen = instelling.bevindingen_da_test
            
            else:
                bevindingen = instelling.bevindingen_da
            
            if len(bevindingen) == 0:
                pass
            else:
                bevindingen = self.splits_controle_omschrijving(bevindingen)
                bevindingen['verklaring'] = ''

                # Check of de controle/norm in de standaardverschillen van de instelling voorkomt
                for i in range(len(bevindingen)):
                    entry = bevindingen.iloc[i, :]

                    # Als de controle/norm hierin voorkomt krijgt deze de verklaring 'standaardverschil'
                    if entry['kenmerk'] in set(HardCodedParameters.standaardverschillen_da[instelling.klant_code]):
                        bevindingen.iloc[i,-1] = "Standaardverschil"
                    else:
                        pass
            
            # Vervang het bevindingen_da dataframe voor die met de standaardverschillen
            if test:
                instelling.bevindingen_da_test = bevindingen
            
            else:
                instelling.bevindingen_da = bevindingen
        else:
            pass
        return None
    
    