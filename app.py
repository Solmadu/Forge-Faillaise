
import streamlit as st
import pandas as pd
from collections import defaultdict

st.set_page_config(page_title="Forge Manager", layout="wide")

EXCEL_FILE = "catalogue_forge.xlsx"

@st.cache_data
def load_data():
    xls = pd.ExcelFile(EXCEL_FILE)
    data = {}
    for sheet in xls.sheet_names:
        data[sheet] = pd.read_excel(xls, sheet_name=sheet)
    return data

data = load_data()

st.title("⚒️ Forge Manager")

catalog = []

for sheet_name, df in data.items():
    if sheet_name.lower() in ["armes", "armures"]:
        df = df.fillna("")
        for _, row in df.iterrows():
            catalog.append({
                "sheet": sheet_name,
                "row": row.to_dict()
            })

if "cart" not in st.session_state:
    st.session_state.cart = []

left, right = st.columns([3,1])

with left:
    search = st.text_input("Recherche")

    for idx, item in enumerate(catalog):
        row = item["row"]
        name = str(next(iter(row.values())))

        if search and search.lower() not in name.lower():
            continue

        with st.container(border=True):
            c1, c2 = st.columns([4,1])
            with c1:
                st.subheader(name)
                if "⚡ TOTAL" in row:
                    st.write(f"Prix vente : {row['⚡ TOTAL']}")
            with c2:
                if st.button("Ajouter", key=f"add_{idx}"):
                    st.session_state.cart.append(item)

with right:
    st.header("🛒 Panier")

    total_revenue = 0
    total_cost = 0
    materials = defaultdict(float)

    for i, item in enumerate(st.session_state.cart):
        row = item["row"]
        name = str(next(iter(row.values())))
        st.write(name)

        if "⚡ TOTAL" in row:
            try:
                total_revenue += float(row["⚡ TOTAL"])
            except:
                pass

        if "💰 TOTAL" in row:
            try:
                total_cost += float(row["💰 TOTAL"])
            except:
                pass

        for k, v in row.items():
            if isinstance(v, (int,float)) and v > 0:
                if any(word in str(k).lower() for word in ["lingot","cuir","bois","pierre","os","corindon"]):
                    materials[k] += v

    st.metric("Revenus", round(total_revenue,2))

    if st.button("Valider la commande"):
        st.divider()

        st.subheader("Matériaux nécessaires")

        for mat, qty in materials.items():
            st.write(f"{mat}: {qty}")

        profit = total_revenue - total_cost

        st.divider()
        st.subheader("Résultats")

        st.write(f"Coût matériaux : {total_cost:.2f}")
        st.write(f"Bénéfice : {profit:.2f}")

        if total_revenue > 0:
            margin = profit / total_revenue * 100
            st.write(f"Marge : {margin:.2f}%")
