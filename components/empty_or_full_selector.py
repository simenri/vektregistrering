import streamlit as st

def render_empty_or_full_selector():
    options = ['Empty tank', 'Full tank']
    selector = st.segmented_control('Tank status:', options=options, selection_mode='single', default=None, key=1)
    return selector
