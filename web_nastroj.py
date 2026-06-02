import streamlit as st
import sys
import os

from hledat_kategorie import HeurekaAllInOne

st.set_page_config(
    page_title="Heureka All-In-One SK",
    page_icon="🤖",
    layout="centered"
)

def nacti_nastroj():
    return HeurekaAllInOne()

nastroj = nacti_nastroj()

# 🚀 OPRAVA: Přepínač změněn na SK a EN
jazyk = st.radio(
    "🌐 Language / Jazyk:",
    options=["SK", "EN"],
    horizontal=True
)

# 🚀 ABSOLUTNÍ OPRAVA: Všechny texty jsou teď pouze slovensky nebo anglicky
txt = {
    "title": "🤖 Heureka All-In-One SK",
    "subtitle": "Inteligentné vyhľadávanie kategórií a systémových pravidiel" if jazyk == "SK" else "Smart search for categories and system rules",
    "desc": "Zadajte názov produktu z e-shopu a algoritmus sa postará o zvyšok." if jazyk == "SK" else "Enter the product name from the e-shop and the algorithm will do the rest.",
    "input_label": "📝 Názov produktu z eshopu:" if jazyk == "SK" else "📝 Product name from e-shop:",
    "input_placeholder": "Zadajte názov produktu..." if jazyk == "SK" else "Enter product name...",
    "type_classic": "🔍 Typ vyhľadávania: Klasická zhoda" if jazyk == "SK" else "🔍 Search type: Classic match",
    "select_label": "👉 Vyberte alebo potvrďte finálnu kategóriu:" if jazyk == "SK" else "👉 Select or confirm the final category:",
    "rules_title": "### 📋 Systémové pravidlá pre:" if jazyk == "SK" else "### 📋 System rules for:",
    "structure_label": "**Správna štruktúra názvu:**" if jazyk == "SK" else "**Correct name structure:**",
    "no_rule": "Pre túto kategóriu nie je definované žiadne špecifické pravidlo v pravidla_sk.txt." if jazyk == "SK" else "No specific rule is defined for this category in pravidla_sk.txt.",
    "params_label": "🚨 **Povinné parametre v XML štruktúre:**" if jazyk == "SK" else "🚨 **Required parameters in XML structure:**",
    "no_param": "Pri tejto kategórii nie je vyžadovaný žiadny povinný parameter." if jazyk == "SK" else "No required parameter is specified for this category.",
    "err_relevant": "❌ Nepodarilo sa nájsť žiadnu dostatočne relevantnú kategóriu. Skúste všeobecnejší názov." if jazyk == "SK" else "❌ No sufficiently relevant category found. Try a more general name.",
    "err_empty": "❌ Nepodarilo sa nájsť žiadnu zodpovedajúcu kategóriu." if jazyk == "SK" else "❌ No matching category found.",
    "all_params_label": "💡 **Odporúčané a voliteľné parametre (Heureka V2):**" if jazyk == "SK" else "💡 **Recommended and optional parameters (Heureka V2):**",
    "no_all_param": "Pre túto kategóriu nie sú v Heureka V2 definované žiadne ďalšie odporúčané parametre." if jazyk == "SK" else "No additional recommended parameters are defined for this category in Heureka V2.",
    "table_header": "Názov parametra" if jazyk == "SK" else "Parameter name"
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
                        priklad_hodnoty = "Hodnota" if jazyk == "SK" else "Value"
                        
                        if "objem" in p_lower or "volume" in p_lower:
                            priklad_hodnoty = "500 ml"
                        elif "veľkosť" in p_lower or "velkost" in p_lower or "size" in p_lower:
                            priklad_hodnoty = "L"
                        elif "farba" in p_lower or "color" in p_lower or "colour" in p_lower:
                            priklad_hodnoty = "Čierna" if jazyk == "SK" else "Black"
                        elif "váha" in p_lower or "hmotnosť" in p_lower or "hmotnost" in p_lower or "weight" in p_lower:
                            priklad_hodnoty = "1.5 kg"
                        elif "materiál" in p_lower or "material" in p_lower:
                            priklad_hodnoty = "Bavlna" if jazyk == "SK" else "Cotton"
                        elif "šírka" in p_lower or "sirka" in p_lower or "width" in p_lower or "výška" in p_lower or "vyska" in p_lower or "height" in p_lower:
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
                
                # --- PREHĽADNÝ ROLOVACÍ BOX PRE V2 ---
                st.write("")  
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
                        
        else:
            st.error(txt["err_relevant"])
    else:
        st.error(txt["err_empty"])