import streamlit as st


def dashboard():
    st.title(f"Bienvenue, {st.session_state['username']} !")
    st.write("Vous êtes maintenant connecté à DriveConnect.")
