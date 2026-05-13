# app.py

```python
import streamlit as st
from PIL import Image
import numpy as np
import cv2
import img2pdf
import tempfile
import os
from io import BytesIO

st.set_page_config(page_title="Document Scanner", layout="centered")

st.title("📄 Adobe Scan Style Document Scanner")
st.write(
    "Upload an image or document photo. The app removes plastic glare/reflections, enhances the document, and converts it into a downloadable PDF."
)


def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped


def remove_glare_and_enhance(image):
    # Convert to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # CLAHE for brightness correction
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    enhanced_lab = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    # Reduce glare / plastic reflections
    hsv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    glare_mask = cv2.threshold(v, 230, 255, cv2.THRESH_BINARY)[1]
    glare_removed = cv2.inpaint(enhanced, glare_mask, 7, cv2.INPAINT_TELEA)

    return glare_removed


def detect_document(image):
    ratio = image.shape[0] / 500.0
    orig = image.copy()

    resized = cv2.resize(image, (int(image.shape[1] / ratio), 500))

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    edged = cv2.Canny(gray, 75, 200)

    contours, _ = cv2.findContours(
        edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )

    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    screen_contour = None

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            screen_contour = approx
            break

    if screen_contour is None:
        return orig

    warped = four_point_transform(
        orig,
        screen_contour.reshape(4, 2) * ratio
    )

    return warped


def scan_document(image):
    detected = detect_document(image)

    glare_removed = remove_glare_and_enhance(detected)

    gray = cv2.cvtColor(glare_removed, cv2.COLOR_BGR2GRAY)

    scanned = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2,
    )

    return scanned


uploaded_file = st.file_uploader(
    "Upload Image",
    type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    st.subheader("Original Image")
    st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), use_container_width=True)

    if st.button("✨ Scan & Remove Plastic Reflections"):
        with st.spinner("Processing document..."):
            scanned = scan_document(image)

            st.subheader("Scanned Output")
            st.image(scanned, clamp=True, use_container_width=True)

            # Save temporary image
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            cv2.imwrite(temp_img.name, scanned)

            # Convert to PDF
            pdf_bytes = img2pdf.convert(temp_img.name)

            pdf_buffer = BytesIO(pdf_bytes)

            st.download_button(
                label="📥 Download PDF",
                data=pdf_buffer,
                file_name="scanned_document.pdf",
                mime="application/pdf",
            )

            os.unlink(temp_img.name)


st.markdown("---")
st.caption("Built with Streamlit + OpenCV")
```

# requirements.txt

```txt
streamlit
opencv-python-headless
numpy
Pillow
img2pdf
```

# Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

# GitHub + Streamlit Cloud Deployment

1. Push `app.py` and `requirements.txt` to your GitHub repository.
2. Open Streamlit Cloud.
3. Connect your GitHub repo.
4. Select `app.py` as the main file.
5. Deploy.

# Features

* Upload document images
* Detect document edges automatically
* Remove plastic glare/reflections
* Enhance readability like Adobe Scan
* Convert scanned image to PDF
* Download processed PDF

