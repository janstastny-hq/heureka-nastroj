import sys
import os

# Naimportujeme velký motor z hledat_kategorie.py
from hledat_kategorie import HeurekaAllInOne

# Zjistí přesnou cestu ke složce
AKTUALNI_SLOZKA = os.path.dirname(os.path.abspath(__file__))

def vypis_detaily_kategorie(cesta, nastroj):
    """Vypíše detailní pravidla pro vybranou cestu."""
    koncova_kat = cesta.split('|')[-1].strip()
    
    print(f"\n📁 DETAIL PRO KATEGORII: {cesta}")
    print(f"📋 SYSTÉMOVÁ PRAVIDLA PRO: {koncova_kat}")
    print("-" * 50)
    
    # Vytáhneme pravidla a parametry z DB
    pravidlo_text = nastroj.najdi_nejlepsi_shodu_v_db(koncova_kat.lower(), nastroj.pravidla_db)
    parametry_text = nastroj.najdi_nejlepsi_shodu_v_db(koncova_kat.lower(), nastroj.parametry_db)
    
    if pravidlo_text:
        print(f"📝 POVINNÝ NÁZEV:\n  {pravidlo_text}")
    else:
        print("📝 POVINNÝ NÁZEV: Pro tuto sekci není definováno specifické pravidlo.")
        
    if parametry_text and parametry_text.strip():
        print(f"⚙️ POVINNÉ PARAMETRY (XML tag <PARAM>):")
        for param in parametry_text.split(','):
            if param.strip():
                print(f"  - {param.strip()}")
    else:
        print("⚙️ POVINNÉ PARAMETRY: Pro tuto sekci Heureka nevyžaduje žádné specifické parametry.")
    print("-" * 50)

if __name__ == "__main__":
    print("\n" + "="*55)
    print("   HEUREKA VALIDÁTOR: SEZNAM KATEGORIÍ -> TEXTOVÝ VÝBĚR")
    print("="*55)
    
    # Nastartujeme velký včerejší motor
    nastroj = HeurekaAllInOne()
    
    while True:
        dotaz = input("\n📝 Zadejte hledaný produkt (nebo 'q' pro konec): ").strip()
        if dotaz.lower() == 'q':
            print("Ukončuji nástroj. Ať se daří!")
            sys.exit()
            
        if not dotaz:
            continue
            
        print(f"\n--- VÝSLEDKY VYHLEDÁVÁNÍ PRO: '{dotaz}' ---")
        
        # Spustíme skloňování a hledání shod
        vsechny_shody = nastroj.vyhledej_presnou_logikou(dotaz)
        
        # Pustíme dál jen ty, co mají body větší nebo rovno 20
        relevantni_shody = [s for s in vsechny_shody if s.get('shody', 0) >= 20]
        top_shody = relevantni_shody[:10]
        
        if top_shody:
            print(f"👉 Nalezené relevantní kategorie:")
            for shoda in top_shody:
                print(f"  - {shoda['cesta']}")
                
            # Druhý krok: Člověk napíše název nebo koncovou kategorii
            while True:
                volba = input("\n✍️ Napište název vybrané kategorie (nebo Enter pro první možnost): ").strip()
                
                if volba == "":
                    vybrana_cesta = top_shody[0]['cesta']
                    break
                
                # Zkusíme najít shodu v textu cesty
                nalezena_cesta = None
                volba_lower = volba.lower()
                
                for shoda in top_shody:
                    if volba_lower in shoda['cesta'].lower():
                        nalezena_cesta = shoda['cesta']
                        break
                
                if nalezena_cesta:
                    vybrana_cesta = nalezena_cesta
                    break
                else:
                    print(f"❌ Tento název neodpovídá žádné z vypsaných kategorií. Zkuste to znovu.")
            
            # Vyhodíme detaily pro spárovanou kategorii
            vypis_detaily_kategorie(vybrana_cesta, nastroj)
            
        else:
            print("⚠️ Pro tento výraz nebyla nalezena žádná dostatečně relevantní kategorie.")
            print("💡 TIP: Zkuste zadat obecnější název produktu.")