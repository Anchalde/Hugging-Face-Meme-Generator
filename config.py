import os

class Config:
    STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "your_stability_api_key_here")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "your_huggingface_api_key_here")

    STABILITY_API_URL = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
    HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

    GENERATED_MEME_DIR = "generated_memes"
    FONT_PATH = "arial.ttf"  # Ensure this font file is available
    IMAGE_SIZE = (768, 768)