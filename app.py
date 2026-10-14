
import streamlit as st
from PIL import Image
from multiprocessing import Pool
import io
import time

st.set_page_config(page_title="Distributed Image Processing",
                   page_icon="🖼️", layout="wide")

st.title("🖼️ Distributed Image Processing System")
st.write("Upload an image, process it using multiple workers, and download the result.")

# Each worker processes one section of the image
def process_section(data):
    index, section = data
    result = section.convert("L")
    return index, result

def process_image(image):
    width, height = image.size

    # Divide image into four sections
    boxes = [
        (0, 0, width // 2, height // 2),
        (width // 2, 0, width, height // 2),
        (0, height // 2, width // 2, height),
        (width // 2, height // 2, width, height)
    ]

    tasks = []
    for i, box in enumerate(boxes):
        tasks.append((i + 1, image.crop(box)))

    # Process sections in parallel
    with Pool(processes=4) as pool:
        results = pool.map(process_section, tasks)

    # Combine the processed sections
    output = Image.new("L", (width, height))
    for index, section in results:
        output.paste(section, boxes[index - 1])

    return output

# Upload image
uploaded_file = st.file_uploader(
    "Choose an image from your computer",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    original = Image.open(uploaded_file).convert("RGB")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Image")
        st.image(original, width="stretch")

    if st.button("⚙️ Process Image", type="primary"):
        with st.spinner("Workers are processing image sections..."):
            start = time.time()
            result = process_image(original)
            elapsed = time.time() - start

        st.session_state["result"] = result
        st.session_state["elapsed"] = elapsed

    if "result" in st.session_state:
        result = st.session_state["result"]

        with col2:
            st.subheader("Processed Image")
            st.image(result, width="stretch")

        st.success("Image processed successfully!")
        st.write(f"Processing time: {st.session_state['elapsed']:.3f} seconds")

        # Prepare image for download
        buffer = io.BytesIO()
        result.save(buffer, format="PNG")

        st.download_button(
            "⬇️ Download Processed Image",
            data=buffer.getvalue(),
            file_name="processed_image.png",
            mime="image/png"
        )
