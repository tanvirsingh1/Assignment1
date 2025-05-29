import streamlit as st
from PIL import Image
import numpy as np
from mini_photo_editor import *
from io import BytesIO


st.title("🖼️Photo Editor")

# Basic Controls - Uploading Image, Undo Image, and History Logs.
with st.sidebar:
    my_img = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if my_img:
        image = to_bgr(Image.open(my_img))  ## PIL Uses RGB color, and OpenCV work with BGR. Hence, conversion is needed.

        #Two Keys
        # Stack-> For saving different image states (for undo).
        # log-> For saving history logs.

        if 'stack' not in st.session_state or not st.session_state.stack:
            st.session_state.stack = [image.copy()]
            st.session_state.log = []
    
    st.write("---")
    
    #///////////////////////////// MAIN SIDE CONTROLS /////////////////////////////////////////////////
    if st.button("Undo"):
        if len(st.session_state.stack) > 1:
            st.session_state.stack.pop()
            st.session_state.log.append("undo pressed.")
            st.session_state.current_tab = 0

        else:
            st.warning("Nothing to undo.")

    if st.button("History"):
        st.code("\n".join(st.session_state.log) if st.session_state.log else "No history yet.")

    st.write("---")
    st.subheader("💾 Save your Edited Image")

    filename = st.text_input("Enter filename (without extension)", value="my_image")
    file_format = st.selectbox("Choose format", ["PNG", "JPEG"])
    if 'stack' in st.session_state and st.session_state.stack:
        latest_image = st.session_state.stack[-1]
        pil_image = Image.fromarray(to_rgb(latest_image))
        buf = BytesIO()
        pil_image.save(buf, format=file_format)
        buf.seek(0)

        st.download_button(
            label="Download Image",
            data=buf,
            file_name=f"{filename}.{file_format.lower()}",
            mime=f"image/{file_format.lower()}"
        )

   
    #/////////////////////////////////////////////////////////////////////////////////////////////////



# Main Window
if 'stack' in st.session_state and st.session_state.stack:
    current_img = st.session_state.stack[-1].copy()

    # Tabs for controls horizontally
    tabs = st.tabs(["Brightness", "Contrast", "Grayscale", "Padding", "Thresholding", "Blending"])
    img2 = None


    # Brightness tab
    with tabs[0]:
        b = st.slider("Brightness", -100, 100, 0)
        if st.button("Apply Brightness"):
            current_img = adjust_brightness(current_img, b)  # contrast=0 means no contrast change
            st.session_state.stack.append(current_img.copy())
            st.session_state.log.append(f"brightness {b}")

    # Contrast tab
    with tabs[1]:
        c = st.slider("Contrast (alpha)", 0.0, 3.0, 1.0, 0.01)
        if st.button("Apply Contrast"):
            current_img = adjust_contrast(current_img, c) 
            st.session_state.stack.append(current_img.copy())
            st.session_state.log.append(f"contrast {c}")

    # Convert to GreyScale
    with tabs[2]:
        if st.button("Convert to Gray_Scale"):
            current_img = convert_grayscale(current_img) 
            st.session_state.stack.append(current_img.copy())
            st.session_state.log.append(f"Converted To Grey Scale")

    # Padding tab
    with tabs[3]:
        p = st.slider("Padding size", 0, 100, 0)
        bt = st.selectbox("Border type", ["constant", "reflect", "replicate", "wrap"])
        rt = st.selectbox("Aspect Ratio", ["none", "square", "rectangle", "custom"])
        custom = st.text_input("Custom ratio (e.g. 4:5)") if rt == "custom" else None
        if st.button("Apply Padding"):
            current_img = adjust_padding(current_img, p, bt, rt if rt != "none" else None, custom)
            st.session_state.stack.append(current_img.copy())
            st.session_state.log.append(f"padded {p}px with {bt} ratio={rt}")

    # Thresholding tab
    with tabs[4]:
        thresh = st.slider("Threshold value", 0, 255, 127)
        mode = st.selectbox("Mode", ["binary", "binary_inv"])
        if st.button("Apply Threshold"):
            current_img = threshold_image(current_img, thresh, mode)
            st.session_state.stack.append(current_img.copy())
            st.session_state.log.append(f"threshold {mode} @ {thresh}")

    # Blending tab
    with tabs[5]:
        blend_file = st.file_uploader("Upload second image", key="blend")
        alpha = st.slider("Alpha", 0.0, 1.0, 0.5)
        if blend_file is not None:
            img2 = to_bgr(Image.open(blend_file))
        if blend_file and st.button("Apply Blending"):
            current_img = blend_images(current_img, img2, alpha)
            st.session_state.stack.append(current_img.copy())
            st.session_state.log.append(f"blended with alpha={alpha}")

    # images side by side
    
    st.subheader("Image Comparison")
    if img2 is not None:
        col1, col2, col3 = st.columns(3) 
        col1.image(to_rgb(st.session_state.stack[0]), caption="Original", use_container_width=True)
        col2.image(to_rgb(img2), caption="Second Image", use_container_width=True)
        col3.image(to_rgb(current_img), caption="Blended", use_container_width=True)
    else:
        col1, col2 = st.columns(2)
        col1.image(to_rgb(st.session_state.stack[0]), caption="Original", use_container_width=True)
        col2.image(to_rgb(current_img), caption="Edited", use_container_width=True)


else:
    st.write("Please upload an image to begin.")
