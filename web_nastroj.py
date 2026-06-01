import streamlit as st
import sys
import os

# Naimportujeme ten opravený dlouhý motor se skloňováním
from hledat_kategorie import HeurekaAllInOne

# Nastavení vzhledu stránky
st.set_page_config(
    page_title="Heureka All-In-One",
    page_icon="🤖",
    layout="centered"
)

@st.cache_resource
def nacti_nastroj():
    return HeurekaAllInOne()

nastroj = nacti_nastroj()

# Hlavní nadpisy vizuálu
st.title("🤖 Heureka All-In-One")
st.subheader("Chytré vyhledávání kategorií a systémových pravidel")
st.write("Zadejte název produktu z e-shopu a algoritmus se postará o zbytek.")

st.divider()

# Vyhledávací pole pro produkt
produkt_input = st.text_input("📝 Název produktu z eshopu:", placeholder="Zadejte název produktu...")

if produkt_input.strip():
    shody = nastroj.vyhledej_presnou_logikou(produkt_input.strip())
    
    if shody:
        st.info("🔍 Typ hledání: Klasická shoda")
        
        relevantni_shody = [s for s in shody if s.get('shody', 0) >= 20]
        top_shody = relevantni_shody[:10]
        
        if top_shody:
            seznam_kategorii = [shoda['cesta'] for shoda in top_shody]
            vybrana_cesta = st.selectbox("👉 Vyberte nebo potvrďte finální kategorii:", seznam_kategorii)
            
            if vybrana_cesta:
                st.divider()
                koncova_kat = vybrana_cesta.split('|')[-1].strip()
                
                pravidlo_text = nastroj.najdi_nejlepsi_shodu_v_db(koncova_kat.lower(), nastroj.pravidla_db)
                parametry_text = nastroj.najdi_nejlepsi_shodu_v_db(koncova_kat.lower(), nastroj.parametry_db)
                
                st.markdown(f"### 📋 Systémová pravidla pro: `{koncova_kat}`")
                
                # Žlutý box pro správnou strukturu názvu
                if pravidlo_text:
                    st.warning(f"**Správná struktura názvu:** {pravidlo_text}")
                else:
                    st.info("Pro tuto kategorií není definováno žádné specifické pravidlo v pravidla.txt.")
                
                # Zervený nebo zelený box pro parametry
                if parametry_text and parametry_text.strip():
                    st.error("**Povinné parametry v XML struktuře:**")
                    
                    for param in parametry_text.split(','):
                        p_cisty = param.strip()
                        if not p_cisty:
                            continue
                        
                        # CHYTRÝ GENERÁTOR UKÁZKY HODNOTY
                        p_lower = p_cisty.lower()
                        priklad_hodnoty = "Hodnota"  # Výchozí univerzální hodnota
                        
                        if "objem" in p_lower:
                            priklad_hodnoty = "500 ml"
                        elif "velikost" in p_lower:
                            priklad_hodnoty = "L"
                        elif "barva" in p_lower:
                            priklad_hodnoty = "Černá"
                        elif "váha" in p_lower or "hmotnost" in p_lower:
                            priklad_hodnoty = "1.5 kg"
                        elif "materiál" in p_lower:
                            priklad_hodnoty = "Bavlna"
                        elif "šířka" in p_lower or "výška" in p_lower or "hloubka" in p_lower:
                            priklad_hodnoty = "60 cm"
                        
                        # Vykreslení krásného formátovaného XML kódu
                        xml_ukazka = f"""```xml
<PARAM>
  <PARAM_NAME>{p_cisty}</PARAM_NAME>
  <VAL>{priklad_hodnoty}</VAL>
</PARAM>
```"""
                        st.markdown(f"**{p_cisty}:**")
                        st.markdown(xml_ukazka)
                        
                else:
                    st.success("U této kategorie není vyžadován žádný povinný parametr.")
        else:
            st.error("❌ Nepodařilo se najít žádnou dostatečně relevantní kategorii. Zkuste obecnější název.")
    else:
        st.error("❌ Nepodařilo se najít žádnou odpovídající kategorii.")