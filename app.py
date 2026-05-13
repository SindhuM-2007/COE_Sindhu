import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="Scanned PDF with Background", layout="centered")
st.title("✨ Scanned PDF Creator with Beautiful Background")
st.write("Upload your document or image, and it will be converted to a PDF with a beautiful background!")

uploaded_file = st.file_uploader("Upload an Image or Document", type=["png", "jpg", "jpeg"])

def add_background(image, bg_color=(240, 248, 255)):
    """
    Adds a beautiful background behind the uploaded image.
    Default is a light pastel blue background.
    """
    # Convert to grayscale
    gray = ImageOps.grayscale(image)

    # Enhance contrast
    contrast = ImageEnhance.Contrast(gray).enhance(2.5)

    # Sharpen
    sharp = contrast.filter(ImageFilter.SHARPEN)

    # Black & white
    bw = sharp.point(lambda x: 0 if x < 140 else 255, '1').convert("RGB")

    # Create background
    bg = Image.new("RGB", (bw.width + 40, bw.height + 40), bg_color)

    # Paste the scanned document onto background (centered)
    bg.paste(bw, (20, 20))

    return bg

def create_pdf(image):
    """
    Converts the final image into a PDF
    """
    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    image.save(temp_img.name)

    pdf = FPDF()
    pdf.add_page()

    img_width, img_height = image.size

    # Fit to A4 width
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

    if st.button("✨ Create Scanned PDF"):
        final_img = add_background(image)

        st.subheader("Preview with Background")
        st.image(final_img, use_container_width=True)

        pdf_file_path = create_pdf(final_img)

        with open(pdf_file_path, "rb") as pdf_file:
            st.download_button(
                label="⬇ Download PDF",
                data=pdf_file,
                file_name="beautiful_scanned_document.pdf",
                mime="application/pdf"
            )

        os.remove(pdf_file_path)
