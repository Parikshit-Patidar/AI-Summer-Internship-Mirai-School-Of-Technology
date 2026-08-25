# AI Image Studio - upgraded version
# MirAI virtual internship - weekend assignment
#
# fixed the width/height bug, the missing .png extension, and added
# magic enhance + surprise me on top of the original prototype

import streamlit as st
import requests
import random
import urllib.parse

st.set_page_config(page_title="AI Image Studio", page_icon="🎨", layout="centered")

st.title("🎨 AI Image Studio")
st.caption("Type a prompt, pick a style, generate an image.")

# a handful of prompts for when someone has writer's block - task 4
SURPRISE_PROMPTS = [
    "An astronaut riding a horse on Mars",
    "A cyberpunk street food vendor in Tokyo",
    "A dragon made entirely of stained glass sleeping on a cloud",
    "A underwater library where fish read books made of coral",
    "A steampunk owl mechanic fixing a clockwork robot in a treehouse workshop",
]

with st.sidebar:
    st.header("Settings")
    art_style = st.selectbox(
        "Art style",
        ["Realistic", "Anime", "Oil Painting", "Cyberpunk", "Watercolor", "Pixel Art"],
    )
    width = st.slider("Width", 256, 1024, 512, step=64)
    height = st.slider("Height", 256, 1024, 512, step=64)
    magic_enhance = st.checkbox("✨ Enable Magic Enhance")

prompt = st.text_input("Describe what you want to see", placeholder="a lighthouse at sunset")

col1, col2 = st.columns(2)
with col1:
    generate_clicked = st.button("Generate", type="primary", use_container_width=True)
with col2:
    surprise_clicked = st.button("🎲 Surprise Me!", use_container_width=True)


def build_image_url(full_prompt, width, height):
    # task 1 fix - width and height were never actually being sent to the
    # api before, the sliders existed but did nothing. urllib.parse.quote
    # handles spaces/special characters in the prompt so the url is valid
    encoded_prompt = urllib.parse.quote(full_prompt)
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}"


def show_image_and_download(full_prompt, width, height, style_for_filename):
    url = build_image_url(full_prompt, width, height)
    with st.spinner("Generating..."):
        response = requests.get(url)

    if response.status_code == 200:
        st.image(response.content, caption=full_prompt, use_container_width=True)
        st.download_button(
            "⬇ Download image",
            data=response.content,
            # task 2 fix - added .png, and made it dynamic based on style
            # instead of a hardcoded name
            file_name=f"{style_for_filename.lower().replace(' ', '_')}_image.png",
            mime="image/png",
        )
    else:
        st.error(f"Image generation failed (status {response.status_code}). Try again.")


if generate_clicked:
    if not prompt:
        st.warning("Type a prompt first.")
    else:
        full_prompt = f"{prompt}, {art_style} style"

        # task 3 - magic enhance, quietly bolts on quality boost words
        # before generating, only if the box is checked
        if magic_enhance:
            full_prompt += ", masterpiece, 8k resolution, highly detailed, trending on artstation, unreal engine 5 render"

        show_image_and_download(full_prompt, width, height, art_style)

if surprise_clicked:
    # task 4 - pick a random prompt and generate immediately, no typing needed
    random_prompt = random.choice(SURPRISE_PROMPTS)
    full_prompt = f"{random_prompt}, {art_style} style"
    if magic_enhance:
        full_prompt += ", masterpiece, 8k resolution, highly detailed, trending on artstation, unreal engine 5 render"

    st.info(f"Surprise prompt: *{random_prompt}*")
    show_image_and_download(full_prompt, width, height, art_style)