import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="Adobe Scan Clone", layout="centered")

st.title("📄 Adobe Scan Clone")
st.write("Upload a document image and convert it into a black & white scanned PDF.")

uploaded_file = st.file_uploader(
    "Upload an Image",
    type=["png", "jpg", "jpeg"]
)

def scan_effect(image):
    # Convert to grayscale
    gray = ImageOps.grayscale(image)

    # Increase contrast
    contrast = ImageEnhance.Contrast(gray).enhance(2.5)

    # Sharpen image
    sharp = contrast.filter(ImageFilter.SHARPEN)

    # Black & white threshold
    bw = sharp.point(lambda x: 0 if x < 140 else 255, '1')

    return bw.convert("RGB")

def create_pdf(image):
    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    image.save(temp_img.name)

    pdf = FPDF()
    pdf.add_page()

    img_width, img_height = image.size

    pdf_width = 190
    pdf_height = (img_height / img_width) * pdf_width

    pdf.image(temp_img.name, x=10, y=10, w=pdf_width, h=pdf_height)

    pdf_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(pdf_output.name)

    temp_img.close()

    return pdf_output.name

if uploaded_file:
    image = Image.open(uploaded_file)

    st.subheader("Original Image")
    st.image(image, use_container_width=True)

    if st.button("Convert to Scanned PDF"):
        scanned = scan_effect(image)

        st.subheader("Scanned Preview")
        st.image(scanned, use_container_width=True)

        pdf_path = create_pdf(scanned)

        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="⬇ Download PDF",
                data=pdf_file,
                file_name="scanned_document.pdf",
                mime="application/pdf"
            )

        os.remove(pdf_path)
