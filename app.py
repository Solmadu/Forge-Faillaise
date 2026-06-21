import streamlit as st
import pandas as pd
from collections import defaultdict

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Forge Manager", layout="wide")

EXCEL_FILE = "catalogue_forge.xlsx"


# ======================
# DATA LOAD
# ======================
@st.cache_data
def load_data():
    xls = pd.ExcelFile(EXCEL_FILE)
    data = {}

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet).fillna("")
        data[sheet] = df

    return data


data = load_data()


# ======================
# BUILD CATALOG
# ======================
catalog = []

for sheet_name, df in data.items():
    if sheet_name.lower() in ["armes", "armures"]:
        for _, row in df.iterrows():
            catalog.append({
                "sheet": sheet_name,
                "row": row.to_dict()
            })


# ======================
# SESSION STATE
# ======================
if "cart" not in st.session_state:
    st.session_state.cart = {}


# ======================
# HELPERS
# ======================
def get_item_name(row):
    return str(next(iter(row.values())))


def is_material_column(col_name):
    ignored = ["⚡ total", "💰 total", "prix", "vente", "benefice"]
    return str(col_name).lower() not in ignored


def add_to_cart(item, idx):
    item_id = f"{item['sheet']}_{idx}"

    if item_id not in st.session_state.cart:
        st.session_state.cart[item_id] = {"item": item, "qty": 1}
    else:
        st.session_state.cart[item_id]["qty"] += 1


def remove_from_cart(item_id):
    st.session_state.cart[item_id]["qty"] -= 1

    if st.session_state.cart[item_id]["qty"] <= 0:
        del st.session_state.cart[item_id]


def clear_cart():
    st.session_state.cart = {}


# ======================
# UI
# ======================
st.title("⚒️ Forge Manager")

tab1, tab2, tab3, tab4 = st.tabs([
    "⚒️ Catalogue",
    "🛒 Commande",
    "📜 Historique",
    "📊 Statistiques"
])


# ======================
# TAB 1 - CATALOGUE
# ======================
with tab1:

    left, right = st.columns([3, 1])

    # -------- LEFT (catalogue)
    with left:
        search = st.text_input("🔎 Recherche")

        category = st.selectbox(
            "Catégorie",
            ["Toutes", "Armes", "Armures"]
        )

        for idx, item in enumerate(catalog):
            row = item["row"]
            name = get_item_name(row)

            if search and search.lower() not in name.lower():
                continue

            if category != "Toutes" and item["sheet"] != category:
                continue

            with st.container(border=True):
                c1, c2 = st.columns([4, 1])

                with c1:
                    st.subheader(name)

                    if "⚡ TOTAL" in row:
                        st.write(f"💰 Prix : {row['⚡ TOTAL']}")

                with c2:
                    if st.button("Ajouter", key=f"add_{idx}"):
                        add_to_cart(item, idx)

    # -------- RIGHT (cart)
    with right:

        st.header("🛒 Panier")

        if st.button("🗑️ Vider"):
            clear_cart()
            st.rerun()

        total_revenue = 0
        total_cost = 0
        materials = defaultdict(float)

        for item_id, cart_item in st.session_state.cart.items():

            item = cart_item["item"]
            qty = cart_item["qty"]
            row = item["row"]
            name = get_item_name(row)

            col1, col2, col3 = st.columns([4, 1, 1])

            with col1:
                st.write(f"**{name}** x{qty}")

                if "⚡ TOTAL" in row:
                    try:
                        price = float(row["⚡ TOTAL"])
                        st.caption(f"{price:.0f} / unité | {price * qty:.0f} total")
                    except:
                        pass

            with col2:
                if st.button("➕", key=f"plus_{item_id}"):
                    st.session_state.cart[item_id]["qty"] += 1
                    st.rerun()

            with col3:
                if st.button("➖", key=f"minus_{item_id}"):
                    remove_from_cart(item_id)
                    st.rerun()

            # ---- totals
            try:
                if "⚡ TOTAL" in row:
                    total_revenue += float(row["⚡ TOTAL"]) * qty
            except:
                pass

            try:
                if "💰 TOTAL" in row:
                    total_cost += float(row["💰 TOTAL"]) * qty
            except:
                pass

            # ---- materials
            for k, v in row.items():
                if isinstance(v, (int, float)) and v > 0:
                    if is_material_column(k):
                        materials[k] += v * qty

        # -------- SUMMARY
        st.divider()

        profit = total_revenue - total_cost

        c1, c2 = st.columns(2)
        with c1:
            st.metric("💰 Revenus", f"{total_revenue:.0f}")
        with c2:
            st.metric("📈 Bénéfice", f"{profit:.0f}")

        # -------- VALIDATION
        if st.button("✅ Valider la commande"):

            st.success("Commande validée")

            st.subheader("📦 Matériaux nécessaires")

            for mat, qty in materials.items():
                st.write(f"- {mat}: {qty}")

            st.divider()
            st.subheader("📊 Résultat")

            st.write(f"Coût : {total_cost:.2f}")
            st.write(f"Bénéfice : {profit:.2f}")

            if total_revenue > 0:
                margin = profit / total_revenue * 100
                st.write(f"Marge : {margin:.2f}%")


# ======================
# TAB 2 - COMMANDE
# ======================
with tab2:
    st.header("🛒 Commande")
    st.info("Résumé futur des commandes (historique des validations)")


# ======================
# TAB 3 - HISTORIQUE
# ======================
with tab3:
    st.header("📜 Historique")
    st.info("À connecter à une base de données (SQLite recommandé)")


# ======================
# TAB 4 - STATISTIQUES
# ======================
with tab4:
    st.header("📊 Statistiques")
    st.info("Bénéfices, ventes, matériaux, graphiques")
