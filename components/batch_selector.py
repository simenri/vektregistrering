import streamlit as st

def render_batch_selector(todays_batches, todays_date):
    if todays_batches:
        st.write(f"Today's date: {todays_date}")
        selected_batch = st.selectbox("Select a batch number or enter your own:", options=todays_batches + ["Other"])
        
        if selected_batch == "Other":
            return st.text_input("Enter batch number:")
        return selected_batch
    else:
        st.write(f"No batch numbers found for {todays_date}.")
        return st.text_input("Enter batch number:")
