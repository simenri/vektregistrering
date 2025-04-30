if use_camera:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = set_enivronment_variable()
    img_file_detection = st.camera_input("Take a picture of the scale for automatic detection")

    if img_file_detection is not None:
        st.image(img_file_detection)
        
        # Vision API
        image_bytes = img_file_detection.getvalue()
        image = vision.Image(content=image_bytes)
        client = vision.ImageAnnotatorClient()
        response = client.text_detection(image=image)

        texts = response.text_annotations
        if texts:
            detected_text = texts[0].description.strip()
            numbers = re.findall(r'\d+', detected_text)
            if numbers:
                detected_text = ''.join(numbers)
                st.session_state.detected_num = int(detected_text)
                st.success(f"Detected number: {detected_text}")
            else:
                st.warning("No numbers detected in the image.")
                st.session_state.detected_num = 0
        else:
            st.warning("Could not extract any text from the image.")
            st.session_state.detected_num = 0

    weight_input = st.session_state.detected_num
else:
    weight_input = st.number_input("Weight (kg)", value=st.session_state.detected_num, step=1)
