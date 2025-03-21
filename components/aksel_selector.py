import streamlit as st


def render_aksel_selector():
    options = [1,2,3]
    selector = st.segmented_control('Aksel: ', options=options, selection_mode='single', default=None,key=2)
    return selector