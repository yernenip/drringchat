import streamlit as st

class Patients:
    def __init__(self) -> None:
        self.patients = {}
        self.populate_patients()

    def populate_patients(self):
        patients_data = st.secrets["patients"]
        self.patients = dict(patients_data)
