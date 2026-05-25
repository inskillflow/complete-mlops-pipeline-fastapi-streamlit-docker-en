import os

import requests
import streamlit as st

# URL du backend FastAPI :
# - dans Docker Compose, on utilise le NOM DU SERVICE comme hostname
#   (ici "fastapi"), résolu automatiquement par le réseau Docker.
# - en dehors de Docker (test local), on retombe sur localhost:8000.
API_URL = os.getenv("API_URL", "http://fastapi:8000")

OPERATIONS = {
    "Addition (+)": "add",
    "Soustraction (-)": "subtract",
    "Multiplication (×)": "multiply",
    "Division (÷)": "divide",
}

st.set_page_config(page_title="Calculatrice FastAPI + Streamlit", page_icon="🧮")
st.title("Calculatrice — Streamlit ↔ FastAPI")
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

col1, col2 = st.columns(2)
with col1:
    a = st.number_input("Nombre A", value=10.0, step=1.0)
with col2:
    b = st.number_input("Nombre B", value=2.0, step=1.0)

operation_label = st.selectbox("Opération", list(OPERATIONS.keys()))
operation_path = OPERATIONS[operation_label]

if st.button("Calculer", type="primary", use_container_width=True):
    url = f"{API_URL}/{operation_path}/{a}/{b}"
    st.code(f"GET {url}", language="bash")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            st.success(f"Résultat : **{data['result']}**")
            st.json(data)
        else:
            st.error(f"Erreur {response.status_code} : {response.json().get('detail')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Impossible de joindre le backend FastAPI : {e}")
