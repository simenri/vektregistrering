import streamlit as st

def render_proof_image_uploader():
    st.markdown("##### Optional: Upload a proof image (photo of the scale)")
    uploaded_image = st.file_uploader("Take or upload a photo", type=["jpg", "jpeg", "png"])
    
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded image", use_container_width=True)
        st.session_state.uploaded_image = uploaded_image
    else:
        st.session_state.uploaded_image = None
