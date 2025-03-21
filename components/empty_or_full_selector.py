import streamlit as st


def render_empty_or_full_selector():
    options = ['Tom tank', 'Full tank']
    selector = st.segmented_control('Fyllingsgrad: ', options=options, selection_mode='single', default=None,key=1)
    return selector