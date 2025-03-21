import streamlit as st

def render_batch_selector(dagens_batches, todays_date):
    if dagens_batches:
        st.write(f"Dagens dato: {todays_date}")
        valgt_batch = st.selectbox("Velg batchnummer eller skriv inn eget:", options=dagens_batches + ["Annet"])
        
        if valgt_batch == "Annet":
            return st.text_input("Skriv inn batchnummer:")
        return valgt_batch
    else:
        st.write(f"Ingen batchnummer funnet for {todays_date}.")
        return st.text_input("Skriv inn batchnummer:")
