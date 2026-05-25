import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://fastapi:8000")

OPERATIONS = {
    "Addition (+)": "add",
    "Soustraction (-)": "subtract",
    "Multiplication (×)": "multiply",
    "Division (÷)": "divide",
}

st.set_page_config(page_title="Calculatrice + Historique PG", page_icon="🧮", layout="wide")
st.title("Calculatrice — Historique persisté en PostgreSQL (chap30)")
st.caption(f"Backend : `{API_URL}`")

with st.sidebar:
    st.header("État du backend")
    if st.button("Tester la connexion"):
        try:
            r = requests.get(f"{API_URL}/", timeout=3)
            r.raise_for_status()
            st.success("Backend joignable")
            st.json(r.json())
        except Exception as e:
            st.error(f"Backend injoignable : {e}")

tab_calc, tab_history = st.tabs(["Calculer", "Historique"])

with tab_calc:
    col1, col2 = st.columns(2)
    with col1:
        a = st.number_input("Nombre A", value=10.0, step=1.0, key="calc_a")
    with col2:
        b = st.number_input("Nombre B", value=2.0, step=1.0, key="calc_b")

    operation_label = st.selectbox("Opération", list(OPERATIONS.keys()))
    operation_value = OPERATIONS[operation_label]
    payload = {"a": a, "b": b, "operation": operation_value}

    st.subheader("JSON envoyé (body POST)")
    st.json(payload)

    if st.button("Calculer (POST + insert PG)", type="primary", use_container_width=True):
        try:
            response = requests.post(f"{API_URL}/calculate", json=payload, timeout=5)
            if response.status_code == 200:
                data = response.json()
                st.success(f"Résultat : **{data['result']}**  (id={data['id']})")
                st.json(data)
            elif response.status_code == 422:
                st.warning("Erreur de validation Pydantic (422)")
                st.json(response.json())
            else:
                st.error(f"Erreur {response.status_code} : {response.json().get('detail')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Impossible de joindre le backend : {e}")

with tab_history:
    col_a, col_b = st.columns([1, 1])
    with col_a:
        refresh = st.button("Rafraîchir l'historique", use_container_width=True)
    with col_b:
        if st.button("⚠️  Vider l'historique (DELETE)", use_container_width=True):
            try:
                r = requests.delete(f"{API_URL}/history", timeout=5)
                r.raise_for_status()
                st.success(f"Supprimé : {r.json().get('deleted')} ligne(s)")
            except Exception as e:
                st.error(f"Erreur : {e}")

    if refresh or True:
        try:
            r = requests.get(f"{API_URL}/history", params={"limit": 100}, timeout=5)
            r.raise_for_status()
            rows = r.json()
            if not rows:
                st.info("Aucun calcul enregistré pour l'instant. Va dans l'onglet **Calculer** !")
            else:
                df = pd.DataFrame(rows)
                df["created_at"] = pd.to_datetime(df["created_at"])
                df = df[["id", "created_at", "operation", "a", "b", "result"]]
                st.metric("Nombre de calculs en base", len(df))
                st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Impossible de charger l'historique : {e}")
