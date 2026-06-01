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

# --- JAZYKOVÝ PŘEPÍNAČ NAHOŘE ---
jazyk = st.radio(
    "🌐 Language / Jazyk:",
    options=["CZ", "EN"],
    horizontal=True
)

# Definice textů pro rozhraní podle vybraného jazyka
txt = {
    "title": "🤖 Heureka All-In-One" if jazyk == "CZ" else "🤖 Heureka All-In-One",
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
    "err_empty": "❌ Nepodařilo se najít žádnou odpovídající kategorii." if jazyk == "CZ" else "❌ No matching category found."
}

# Hlavní nadpisy vizuálu (používají slovník txt)
st.title(txt["title"])
st.subheader(txt["subtitle"])
st.write(txt["desc"])

st.divider()

# --- PAMĚŤ PRO AUTOMATICKOU OPRAVU TEXTU ---
if "opraveny_text" not in st.session_state:
    st.session_state["opraveny_text"] = ""

# Vyhledávací pole pro produkt propojené s pamětí oprav
produkt_input = st.text_input(
    txt["input_label"], 
    value=st.session_state["opraveny_text"] if st.session_state["opraveny_text"] else "",
    placeholder=txt["input_placeholder"]
)

# --- SAMOTNÉ VYHLEDÁVÁNÍ A ZOBRAZENÍ VÝSLEDKŮ ---
if produkt_input.strip():
    shody = nastroj.vyhledej_presnou_logikou(produkt_input.strip())
    
    # KONTROLA PŘEKLEPŮ: Aktivuje se, POUZE pokud klasické vyhledávání nenašlo vůbec nic
    navrh_opravy = None
    if not shody:
        import difflib
        import unicodedata
        
        def bez_diakritiky(text):
            text_str = str(text).lower()
            return "".join(c for c in unicodedata.normalize('NFD', text_str) if unicodedata.category(c) != 'Mn')
            
        # Vytáhneme slovník slov z Heureky
        vsechna_slova = set()
        slovnik_ascii = {}
        for kat in nastroj.kategorie:
            cesta_cista = kat.replace("|", " ").replace(",", " ").replace(".", " ")
            for s in cesta_cista.split():
                w = s.lower().strip()
                if len(w) >= 3:
                    vsechna_slova.add(w)
                    slovnik_ascii[bez_diakritiky(w)] = w
                    
        slovnik_pro_opravu = list(vsechna_slova)
        slovnik_pro_opravu_ascii = list(slovnik_ascii.keys())
        
        slova_uzivatele = produkt_input.strip().lower().split()
        
        for i, slovo in enumerate(slova_uzivatele):
            if slovo not in slovnik_pro_opravu:
                blizka_shoda = difflib.get_close_matches(slovo, slovnik_pro_opravu, n=1, cutoff=0.60)
                if blizka_shoda:
                    slova_uzivatele[i] = blizka_shoda[0]
                    navrh_opravy = " ".join(slova_uzivatele)
                    break
                else:
                    slovo_ascii = bez_diakritiky(slovo)
                    blizka_shoda_ascii = difflib.get_close_matches(slovo_ascii, slovnik_pro_opravu_ascii, n=1, cutoff=0.60)
                    if blizka_shoda_ascii:
                        slova_uzivatele[i] = slovnik_ascii[blizka_shoda_ascii[0]]
                        navrh_opravy = " ".join(slova_uzivatele)
                        break
                        
        if navrh_opravy and navrh_opravy != produkt_input.strip().lower():
            if st.button(f"💡 Mysleli jste: **{navrh_opravy}**?", type="secondary"):
                st.session_state["opraveny_text"] = navrh_opravy
                st.rerun()

    # Resetujeme mezipaměť, pokud uživatel píše dál ručně a mění zadání
    if produkt_input.strip() and produkt_input.strip() != st.session_state["opraveny_text"]:
        st.session_state["opraveny_text"] = produkt_input.strip()
    
    # Vykreslení výsledků vyhledávání
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
        else:
            st.error(txt["err_relevant"])
    else:
        # Zobrazí se červená chyba vyhledávání, jen když zároveň nevyskočilo tlačítko opravy
        if not navrh_opravy:
            st.error(txt["err_empty"])