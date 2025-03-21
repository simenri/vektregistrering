
encoded_creds = st.secrets["google"]["google_credentials"]
padding = len(encoded_creds) % 4
if padding != 0: # Sjekker om den faktisk opprettholder kravet om at det skal være delelig på fire og legger på padding dersom det ikke er det.
    encoded_creds += "=" * (4 - padding)
creds_json = base64.b64decode(encoded_creds)
with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
    tmp_file.write(creds_json)
    tmp_file_path = tmp_file.name

# Sett miljøvariabelen til den midlertidige filen
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_file_path


img_file = st.camera_input("Ta bilde av vekta")

if img_file is not None:
    # Vis bilde
    st.image(img_file)

    # Lagre bildet midlertidig for Vision API
    image_bytes = img_file.getvalue()
    image = vision.Image(content=image_bytes)

    # Initier Vision-klient
    client = vision.ImageAnnotatorClient()
    response = client.text_detection(image=image)

    texts = response.text_annotations
    if texts:
        # Første element er hele teksten, resten er delene
        detected_text = texts[0].description.strip()
        st.success(f"Oppdaget tall: {detected_text}")
    else:
        st.warning("Fikk ikke tolket noe tall fra bildet.")