import os
import sys
import re

# Vypnuto pro Python 3.14, aby nevznikaly žluté chyby
AI_DOSTUPNA = False

AKTUALNI_SLOZKA = os.path.dirname(os.path.abspath(__file__))
SOUBOR_KATEGORII = os.path.join(AKTUALNI_SLOZKA, 'kategorie.txt')
SOUBOR_PARAMETRU = os.path.join(AKTUALNI_SLOZKA, 'parametry.txt')
SOUBOR_PRAVIDEL = os.path.join(AKTUALNI_SLOZKA, 'pravidla.txt')

class HeurekaAllInOne:
    def __init__(self):
        self.kategorie = []
        self.parametry_db = {}
        self.pravidla_db = {}
        
        self.vytahni_category_fullname()
        self.nacti_txt_databazi(SOUBOR_PARAMETRU, self.parametry_db)
        self.nacti_txt_databazi(SOUBOR_PRAVIDEL, self.pravidla_db)

    def vytahni_category_fullname(self):
        if not os.path.exists(SOUBOR_KATEGORII) or os.path.getsize(SOUBOR_KATEGORII) == 0:
            print(f"❌ CHYBA: Soubor 'kategorie.txt' je prázdný nebo neexistuje.")
            sys.exit()
        try:
            with open(SOUBOR_KATEGORII, 'r', encoding='utf-8', errors='ignore') as f:
                obsah = f.read()
            nalezeno = re.findall(r'<CATEGORY_FULLNAME>(.*?)</CATEGORY_FULLNAME>', obsah, re.DOTALL)
            for cesta in nalezeno:
                cesta_cista = cesta.strip()
                if cesta_cista:
                    self.kategorie.append(cesta_cista)
            self.kategorie = sorted(list(set(self.kategorie)))
            print(f"✅ ÚSPĚCH: Úspěšně načteno {len(self.kategorie)} Heureka cest ze souboru 'kategorie.txt'.")
        except Exception as e:
            sys.exit()

    def nacti_txt_databazi(self, cesta_k_souboru, cilovy_slovnik):
        if not os.path.exists(cesta_k_souboru):
            return
        try:
            with open(cesta_k_souboru, 'r', encoding='utf-8', errors='ignore') as f:
                for radek in f:
                    radek_s = radek.strip()
                    if not radek_s:
                        continue
                    oddelovac = None
                    if '=' in radek_s: oddelovac = '='
                    elif '–' in radek_s: oddelovac = '–'
                    elif '—' in radek_s: oddelovac = '—'
                    elif '-' in radek_s: oddelovac = '-'
                    if oddelovac:
                        klic, hodnota = radek_s.split(oddelovac, 1)
                        cilovy_slovnik[klic.strip().lower()] = hodnota.strip()
            print(f"✅ ÚSPĚCH: Databáze '{os.path.basename(cesta_k_souboru)}' úspěšně načtena ({len(cilovy_slovnik)} záznamů).")
        except Exception as e:
            pass

    def vyhledej_presnou_logikou(self, nazev_produktu):
        nazev_lower = nazev_produktu.lower()
        synonyma = {
            "iphone": "mobilní telefony",
            "ipad": "tablety",
            "airpods": "sluchátka",
            "playstation": "herní konzole",
            "xbox": "herní konzole"
        }

        rozsireny_nazev = nazev_produktu
        for klic, vyznam in synonyma.items():
            if klic in nazev_lower:
                rozsireny_nazev += f" {vyznam}"

        cista_slova = [s.lower() for s in rozsireny_nazev.split() if len(s) >= 2]
        orezana_slova = [self.dej_zaklad_slova(s.lower()) for s in rozsireny_nazev.split() if len(s) >= 2]
        
        if not cista_slova:
            return []

        vysledky = []

        for radek in self.kategorie_db:
            # ČIŠTĚNÍ: Odstraníme XML značky, pokud v řádku jsou, abychom hodnotili jen čistou cestu
            cista_cesta = radek.replace("<CATEGORY_FULLNAME>", "").replace("</CATEGORY_FULLNAME>", "").strip()
            cesta_lower = cista_cesta.lower()
            
            pocet_shod = 0
            # Spočítáme, kolik slov z dotazu se v ČISTÉ cestě nachází
            for i in range(len(cista_slova)):
                if cista_slova[i] in cesta_lower or orezana_slova[i] in cesta_lower:
                    pocet_shod += 1

            if pocet_shod > 0:
                skore = (pocet_shod / len(cista_slova)) * 100
                
                # Sledujeme konec čisté cesty bez XML značek
                koncova_kat = cista_cesta.split('|')[-1].lower()
                
                # Pokud uživatel napsal slovo, které je přímo finální kategorií, získá obří výhodu
                for s in cista_slova:
                    if s in koncova_kat:
                        skore += 300  # Ještě jsme přitopili na +300 bodů
                
                # Penalizace pro doplňky a pouzdra, pokud je uživatel vyloženě nehledá
                if "příslušenství" in koncova_kat or "pouzdra" in koncova_kat or "držáky" in koncova_kat or "kryty" in koncova_kat:
                    if not any(p in cista_slova for p in ["pouzdro", "obal", "kryt", "drzak", "držík", "prislusenstvi"]):
                        skore -= 150  # Drsnější odsunutí doplňků dolů

                vysledky.append({
                    'cesta': cista_cesta,  # Vrátíme už krásnou čistou cestu bez XML tagů!
                    'shody': skore
                })

        vysledky = sorted(vysledky, key=lambda x: x['shody'], reverse=True)
        return vysledky

        # TATO FUNKCE ČISTÍ KONCOVKY SLOV A ZVLÁDÁ SKLOŇOVÁNÍ Z VČEREJŠKA
        def dej_zaklad_slova(slovo):
            slovo = slovo.lower().strip()
            slovo = slovo.replace('í', 'i').replace('é', 'e').replace('ý', 'y').replace('á', 'a').replace('ó', 'o').replace('ú', 'u').replace('ů', 'u')
            if len(slovo) <= 3:
                return slovo
            koncovky = ['ova', 'ove', 'ovy', 'ovou', 'oveho', 'ovemu', 'ovych', 'ovym', 'ovymi', 'ami', 'em', 'ech', 'ich', 'um', 'ou', 'am', 'y', 'e', 'a', 'i', 'o', 'u']
            for koncovka in koncovky:
                if slovo.endswith(koncovka):
                    vysledek = slovo[:-len(koncovka)]
                    if len(vysledek) >= 3:
                        return vysledek
                    break
            return slovo

        zaklady_hledanych_slov = [dej_zaklad_slova(s) for s in puvodni_slova]
        vysledky = []

        for kat in self.kategorie:
            kat_lower = kat.lower()
            casti_cesty = [c.strip().lower() for c in kat_lower.split('|')]
            posledni_sekce = casti_cesty[-1] if casti_cesty else ""
            
            slova_konce_kat = [s.strip() for s in posledni_sekce.split() if len(s) > 2]
            zaklady_konce_kat = [dej_zaklad_slova(s) for s in slova_konce_kat]
            
            body = 0
            pocet_shodnych_slov = 0
            
            for z_slovo in zaklady_hledanych_slov:
                for z_kat in zaklady_konce_kat:
                    if z_slovo == z_kat:
                        body += 40
                        pocet_shodnych_slov += 1
                    elif z_slovo in z_kat or z_kat in z_slovo:
                        body += 20
                        pocet_shodnych_slov += 1

            if pocet_shodnych_slov > 0:
                if pocet_shodnych_slov > 1:
                    body += (pocet_shodnych_slov - 1) * 60
                
                if len(zaklady_konce_kat) == 1:
                    body += 15
                
                for z_kat in zaklady_konce_kat:
                    if z_kat not in zaklady_hledanych_slov:
                        body -= 5

                if body > 0:
                    vysledky.append({
                        "cesta": kat,
                        "shody": body,
                        "jistota_procenta": 100
                    })
        
        return sorted(vysledky, key=lambda x: x['shody'], reverse=True)

    def vyhledej_pomoci_ai(self, nazev_produktu):
        return []

    def najdi_nejlepsi_shodu_v_db(self, slovo_hledane, databaze):
        if slovo_hledane in databaze:
            return databaze[slovo_hledane]
            
        def dej_zaklad_slova(slovo):
            slovo = slovo.lower().strip()
            slovo = slovo.replace('í', 'i').replace('é', 'e').replace('ý', 'y').replace('á', 'a').replace('ó', 'o').replace('ú', 'u').replace('ů', 'u')
            if len(slovo) <= 3:
                return slovo
            koncovky = ['ova', 'ove', 'ovy', 'ovou', 'oveho', 'ovemu', 'ovych', 'ovym', 'ovymi', 'ami', 'em', 'ech', 'ich', 'um', 'ou', 'am', 'y', 'e', 'a', 'i', 'o', 'u']
            for koncovka in koncovky:
                if slovo.endswith(koncovka):
                    vysledek = slovo[:-len(koncovka)]
                    if len(vysledek) >= 3:
                        return vysledek
                    break
            return slovo

        zaklad_hledaneho = dej_zaklad_slova(slovo_hledane)
        
        for klic_db in sorted(databaze.keys(), key=len):
            if klic_db == slovo_hledane or dej_zaklad_slova(klic_db) == zaklad_hledaneho:
                return databaze[klic_db]
                
        for klic_db in sorted(databaze.keys(), key=len):
            zaklaw_db = dej_zaklad_slova(klic_db)
            if zaklad_hledaneho in zaklaw_db or zaklaw_db in zaklad_hledaneho:
                return databaze[klic_db]
                
        return None