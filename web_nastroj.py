import streamlit as st
import sys
import os

from hledat_kategorie import HeurekaAllInOne

st.set_page_config(
    page_title="Heureka All-In-One",
    page_icon="🤖",
    layout="centered"
)

# Smazán @st.cache_resource, aby se databáze natvrdo načetly znovu a nezůstávaly viset v paměti
def nacti_nastroj():
    return HeurekaAllInOne()

nastroj = nacti_nastroj()

jazyk = st.radio(
    "🌐 Language / Jazyk:",
    options=["CZ", "EN"],
    horizontal=True
)

txt = {
    "title": "🤖 Heureka All-In-One",
    "subtitle": "Chytré vyhledávání kategorií a systémových pravidel" if jazyk == "CZ" else "Smart search for categories and system rules",
    "desc": "Zadejte název produktu z e-shopu a algoritmus se postará o zbytek." if jazyk == "CZ" else "Enter the product name from the e-shop and the algorithm will do the rest.",
    "input_label": "📝 Název produktu z eshopu:" if jazyk == "CZ" else "📝 Product name from e-shop:",
    "input_placeholder": "Zadejte název produktu..." if jazyk == "CZ" else "Enter product name...",
    "type_classic": "🔍 Typ hledání: Klasická shoda" if jazyk == "CZ" else "🔍 Search type: Classic match",
    "select_label": "👉 Vyberte nebo potvrďte finální kategorii:" if jazyk == "CZ" else "👉 Select or confirm the final category:",
    "rules_title": "### 📋 Systémová pravidla pro:" if jazyk == "CZ" else "### 📋 System rules for:",
    "structure_label": "**Správná struktura názvu:**" if jazyk == "CZ" else "**Correct name structure:**",
    "no_rule": "Pro tuto kategorii není definováno žádné specifické pravidlo v pravidla.txt." if jazyk == "CZ" else "No specific rule is defined for this category in pravidla.txt.",
    "params_label": "**Povinné parametry v XML struktuře:**" if jazyk == "CZ" else "**Required parameters in XML structure:**",
    "no_param": "U této kategorie není vyžadován žádný povinný parametr." if jazyk == "CZ" else "No required parameter is specified for this category.",
    "err_relevant": "❌ Nepodařilo se najít žádnou dostatečně relevantní kategorii. Zkuste obecnější název." if jazyk == "CZ" else "❌ No sufficiently relevant category found. Try a more general name.",
    "err_empty": "❌ Nepodařilo se najít žádnou odpovídající kategorii." if jazyk == "CZ" else "❌ No matching category found.",
    # Nové texty pro doporučené parametry z V2
    "all_params_label": "💡 **Všechny dostupné a doporučené parametry pro tuto sekci (Heureka V2):**" if jazyk == "CZ" else "💡 **All available and recommended parameters for this section (Heureka V2):**",
    "no_all_param": "Pro tuto kategorii nejsou v databázi definovány žádné další doporučené parametry." if jazyk == "CZ" else "No additional recommended parameters are defined for this category."
}

st.title(txt["title"])
st.subheader(txt["subtitle"])
st.write(txt["desc"])

st.divider()

produkt_input = st.text_input(txt["input_label"], placeholder=txt["input_placeholder"])

if produkt_input.strip():
    shody = nastroj.vyhledej_presnou_logikou(produkt_input.strip())
    
    if shody:
        st.info(txt["type_classic"])
        
        relevantni_shody = [s for s in shody if s.get('shody', 0) >= 20]
        top_shody = relevantni_shody[:10]
        
        if top_shody:
            seznam_kategorii = [shoda['cesta'] for shoda in top_shody]
            vybrana_cesta = st.selectbox(txt["select_label"], seznam_kategorii)
            
            if vybrana_cesta:
                st.divider()
                koncova_kat = vybrana_cesta.split('|')[-1].strip()
                
                pravidlo_text = nastroj.najdi_nejlepsi_shodu_v_db(koncova_kat.lower(), nastroj.pravidla_db)
                parametry_text = nastroj.najdi_nejlepsi_shodu_v_db(koncova_kat.lower(), nastroj.parametry_db)
                
                st.markdown(f"{txt['rules_title']} `{koncova_kat}`")
                
                if pravidlo_text:
                    st.warning(f"{txt['structure_label']} {pravidlo_text}")
                else:
                    st.info(txt["no_rule"])
                
                if parametry_text and parametry_text.strip():
                    st.error(txt["params_label"])
                    
                    for param in parametry_text.split(','):
                        p_cisty = param.strip()
                        if not p_cisty:
                            continue
                        
                        p_lower = p_cisty.lower()
                        priklad_hodnoty = "Hodnota" if jazyk == "CZ" else "Value"
                        
                        if "objem" in p_lower or "volume" in p_lower:
                            priklad_hodnoty = "500 ml"
                        elif "velikost" in p_lower or "size" in p_lower:
                            priklad_hodnoty = "L"
                        elif "barva" in p_lower or "color" in p_lower or "colour" in p_lower:
                            priklad_hodnoty = "Černá" if jazyk == "CZ" else "Black"
                        elif "váha" in p_lower or "hmotnost" in p_lower or "weight" in p_lower:
                            priklad_hodnoty = "1.5 kg"
                        elif "materiál" in p_lower or "material" in p_lower:
                            priklad_hodnoty = "Bavlna" if jazyk == "CZ" else "Cotton"
                        elif "šířka" in p_lower or "width" in p_lower or "výška" in p_lower or "height" in p_lower:
                            priklad_hodnoty = "60 cm"
                        
                        xml_ukazka = f"""```xml
<PARAM>
  <PARAM_NAME>{p_cisty}</PARAM_NAME>
  <VAL>{priklad_hodnoty}</VAL>
</PARAM>
```"""
                        st.markdown(f"**{p_cisty}:**")
                        st.markdown(xml_ukazka)
                        
                else:
                    st.success(txt["no_param"])
                
                # --- NOVÝ MODUL: DOPORUČENÉ PARAMETRY (Z PARAMETRY-V2.TXT VIA POSLEDNÍ SLOVO) ---
                st.write("")  # Drobná estetická mezera
                
                vsechny_parametry_text = None
                koncova_kat_lower = koncova_kat.lower().strip()
                
                # Izolujeme pouze úplně poslední slovo z koncové kategorie (např. z "Řazení na kolo" zbyde "kolo")
                slova_konce = koncova_kat_lower.split()
                posledni_slovo = slova_konce[-1].strip() if slova_konce else ""
                
                # 1. Krok: Hledáme v obří V2 databázi čistě podle tohoto posledního slova (např. "bazény")
                if posledni_slovo in nastroj.vsechny_parametry_db:
                    vsechny_parametry_text = nastroj.vsechny_parametry_db[posledni_slovo]
                else:
                    # 2. Krok: Záložní varianta, pokud by klíč v DB byl víceslovný
                    if koncova_kat_lower in nastroj.vsechny_parametry_db:
                        vsechny_parametry_text = nastroj.vsechny_parametry_db[koncova_kat_lower]
                    else:
                        # 3. Krok: Poslední záchrana – prohledání klíčů přes podřetězec
                        for klic_db in nastroj.vsechny_parametry_db.keys():
                            if posledni_slovo in klic_db or klic_db in posledni_slovo:
                                vsechny_parametry_text = nastroj.vsechny_parametry_db[klic_db]
                                break
                
                if vsechny_parametry_text and vsechny_parametry_text.strip():
                    st.info(txt["all_params_label"])
                    
                    # Rozsekáme parametry podle čárek a očistíme je
                    list_parametru = [p.strip() for p in vsechny_parametry_text.split(',') if p.strip()]
                    
                    # Vykreslíme je přehledně vedle sebe oddělené lomítkem
                    st.markdown(" / ".join([f"`{param}`" for param in list_parametru]))
                else:
                    st.caption(txt["no_all_param"])
                # -------------------------------------------------------------------------------
                        
        else:
            st.error(txt["err_relevant"])
    else:
        st.error(txt["err_empty"])