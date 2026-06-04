import streamlit as st
import sys
import os

from hledat_kategorie import HeurekaAllInOne

st.set_page_config(
    page_title="Heureka All-In-One",
    page_icon="🤖",
    layout="centered"
)

# Bez cache dekorátoru, aby Streamlit natvrdo prohledával čerstvé soubory
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
    "desc": "Zadejte název produktu z e-shopu and algoritmus se postará o zbytek." if jazyk == "CZ" else "Enter the product name from the e-shop and the algorithm will do the rest.",
    "input_label": "📝 Název produktu z eshopu:" if jazyk == "CZ" else "📝 Product name from e-shop:",
    "input_placeholder": "Zadejte název produktu..." if jazyk == "CZ" else "Enter product name...",
    "type_classic": "🔍 Typ hledání: Klasická shoda" if jazyk == "CZ" else "🔍 Search type: Classic match",
    "select_label": "👉 Vyberte nebo potvrďte finální kategorii:" if jazyk == "CZ" else "👉 Select or confirm the final category:",
    "rules_title": "### 📋 Systémová pravidla pro:" if jazyk == "CZ" else "### 📋 System rules for:",
    "structure_label": "**Správná struktura názvu:**" if jazyk == "CZ" else "**Correct name structure:**",
    "no_rule": "Pro tuto kategorií není definováno žádné specifické pravidlo v pravidla.txt." if jazyk == "CZ" else "No specific rule is defined for this category in pravidla.txt.",
    "params_label": "🚨 **Povinné parametry v XML struktuře:**" if jazyk == "CZ" else "🚨 **Required parameters in XML structure:**",
    "no_param": "U této kategorie není vyžadován žádný povinný parametr." if jazyk == "CZ" else "No required parameter is specified for this category.",
    "err_relevant": "❌ Nepodařilo se najít žádnou dostatečně relevantní kategorii. Zkuste obecnější název." if jazyk == "CZ" else "❌ No sufficiently relevant category found. Try a more general name.",
    "err_empty": "❌ Nepodařilo se najít žádnou odpovídající kategorii." if jazyk == "CZ" else "❌ No matching category found.",
    "all_params_label": "💡 **Doporučené a volitelné parametry (Heureka V2):**" if jazyk == "CZ" else "💡 **Recommended and optional parameters (Heureka V2):**",
    "no_all_param": "Pro tuto kategorii nejsou v Heureka V2 definovány žádné další doporučené parametry." if jazyk == "CZ" else "No additional recommended parameters are defined for this category in Heureka V2.",
    "table_header": "Obecný název produktu" if jazyk == "CZ" else "General product name",
    # Texty pro modul hodnocení
    "rating_title": "### ⭐ Ohodnoťte náš nástroj" if jazyk == "CZ" else "### ⭐ Rate our tool",
    "rating_comment_label": "Máte pro nás vzkaz nebo nápad na zlepšení?" if jazyk == "CZ" else "Do you have a message or an idea for improvement?",
    "rating_comment_placeholder": "Napište nám..." if jazyk == "CZ" else "Write to us...",
    "rating_button": "Odeslat hodnocení" if jazyk == "CZ" else "Submit rating",
    "rating_success": "🎉 Děkujeme! Vaše hodnocení bylo úspěšně uloženo." if jazyk == "CZ" else "🎉 Thank you! Your rating has been successfully saved.",
    "rating_warning": "Prosím, vyberte nejdříve počet hvězdiček." if jazyk == "CZ" else "Please select a star rating first.",
    # Správcovské texty (Anonymní bez jména)
    "admin_panel_title": "📊 Správa nástroje" if jazyk == "CZ" else "📊 Tool Administration",
    "admin_password_label": "Zadejte správcovské heslo:" if jazyk == "CZ" else "Enter admin password:",
    "admin_wrong_password": "❌ Nesprávné heslo!" if jazyk == "CZ" else "❌ Incorrect password!"
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
                vsechny_parametry_text = nastroj.najdi_nejlepsi_shodu_v_db(koncova_kat.lower(), nastroj.vsechny_parametry_db)
                
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
                        elif "šírka" in p_lower or "width" in p_lower or "výška" in p_lower or "height" in p_lower:
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
                
                # --- NOVÝ PŘEHLEDNÝ ROLOVACÍ BOX PRO V2 ---
                st.write("")  # Mezera pro přehlednost
                st.info(txt["all_params_label"])
                
                if vsechny_parametry_text and vsechny_parametry_text.strip():
                    list_parametru = [p.strip() for p in vsechny_parametry_text.split(',') if p.strip()]
                    st.dataframe(
                        {txt["table_header"]: list_parametru},
                        use_container_width=True,
                        height=380,
                        hide_index=True
                    )
                else:
                    st.caption(txt["no_all_param"])
                # -------------------------------------------------------------------------------
                        
        else:
            st.error(txt["err_relevant"])
    else:
        st.error(txt["err_empty"])

# ===============================================================================
# ⭐ MODUL PRO HODNOCENÍ NÁSTROJE (Klikací hvězdičky uvnitř formuláře s pojistkou)
# ===============================================================================
st.divider()
st.write(txt["rating_title"])

# Definujeme název souboru pro ukládání hodnocení ve stejné složce
SOUBOR_HODNOCENI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "historie_hodnoceni.txt")

# Zabalení hodnocení do formuláře
with st.form("formular_hodnoceni", clear_on_submit=True):
    
    hodnoceni = st.feedback("stars", key="kliknute_hvezdicky")
    
    komentar = st.text_area(
        txt["rating_comment_label"], 
        placeholder=txt["rating_comment_placeholder"],
        key="kliknuty_komentar"
    )
    
    odeslano = st.form_submit_button(txt["rating_button"])
    
    if odeslano:
        if hodnoceni is not None:
            pocet_hvezdicek = hodnoceni + 1
            hvezdy_text = "⭐" * pocet_hvezdicek + f" ({pocet_hvezdicek}/5)"
            
            cisty_komentar = komentar.strip() if komentar.strip() else "Bez textového komentáře."
            radek_k_zapisu = f"Hodnocení: {hvezdy_text} | Jazyk: {jazyk} | Vzkaz: {cisty_komentar}\n"
            
            try:
                with open(SOUBOR_HODNOCENI, "a", encoding="utf-8") as f:
                    f.write(radek_k_zapisu)
                st.success(txt["rating_success"])
            except Exception as e:
                st.error(f"Chyba při ukládání: {e}")
        else:
            st.warning(txt["rating_warning"])

# 📊 ANONYMNÍ SKRYTÝ ROZBALOVACÍ PANEL ZABEZPEČENÝ HESLEM
st.write("")
with st.expander(txt["admin_panel_title"]):
    heslo = st.text_input(txt["admin_password_label"], type="password", key="sprava_heslo")
    
    if heslo == "Bandyta12":
        if os.path.exists(SOUBOR_HODNOCENI):
            try:
                with open(SOUBOR_HODNOCENI, "r", encoding="utf-8") as f:
                    zaznamy = f.readlines()
                
                if zaznamy:
                    st.write(f"### 📋 Získaná hodnocení (Celkem: {len(zaznamy)}):")
                    for zr in reversed(zaznamy):
                        if zr.strip():
                            st.code(zr.strip(), language="text")
                else:
                    st.info("Historie hodnocení je zatím prázdná." if jazyk == "CZ" else "Rating history is empty.")
            except Exception as e:
                st.error(f"Chyba při čtení: {e}")
        else:
            st.info("Zatím nikdo neodeslal žádné hodnocení." if jazyk == "CZ" else "No ratings submitted yet.")
    elif heslo != "":
        st.error(txt["admin_wrong_password"])