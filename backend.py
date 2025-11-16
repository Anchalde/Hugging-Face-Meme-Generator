import os
import requests
import io
from typing import Optional
from config import Config
import logging

# Set up logging for better error and status messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MemeGenerator:
    """
    A class to generate images based on a given situation.
    """

    def __init__(self):
        """
        Initializes the MemeGenerator with API configurations.
        """
        # Removed Groq client initialization as caption generation is removed
        self.headers = {"Authorization": f"Bearer {Config.HUGGINGFACE_API_KEY}"}
        
        # This will hold the local Stable Diffusion pipeline after it's first loaded
        self._sd_pipeline = None

    def _build_image_prompt(self, situation: str, style: str) -> str:
        """
        Builds a detailed image generation prompt.
        """
        # The prompt is now directly for the image, not a meme with a caption
        return (
    f"A simple, humorous illustration in a {style} style, "
    f"like a WhatsApp sticker or classic internet meme. "
    f"and flat colors, clearly depicting the situation: '{situation}'. "
    f"Focus on a single, clear subject with a minimalist or transparent background. "
)
    
    def _generate_with_local_sd(self, prompt: str) -> Optional[bytes]:
        """
        Generates an image using a local Stable Diffusion model.
        This method requires `diffusers`, `torch`, and a compatible GPU.
        """
        try:
            from diffusers import StableDiffusionPipeline
            import torch
            
            # Initialize the pipeline (cache after first load)
            if self._sd_pipeline is None:
                logger.info("Loading local Stable Diffusion model...")
                # Use a model that balances quality and VRAM usage.
                model_id = "runwayml/stable-diffusion-v1-5"
                device = "cuda" if torch.cuda.is_available() else "cpu"
                torch_dtype = torch.float16 if device == "cuda" else torch.float32

                self._sd_pipeline = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch_dtype,
                ).to(device)
                
                logger.info(f"Using local Stable Diffusion on device: {device}")

            # Generate the image
            with torch.no_grad():
                image_pil = self._sd_pipeline(prompt, num_inference_steps=25).images[0]

            # Convert PIL Image to bytes
            output_buffer = io.BytesIO()
            image_pil.save(output_buffer, format='PNG')
            return output_buffer.getvalue()

        except ImportError:
            logger.warning("Diffusers or PyTorch not installed. Local SD generation is not available.")
            return None
        except Exception as e:
            logger.error(f"Local Stable Diffusion error: {e}")
            return None

    def _generate_with_stability_ai(self, prompt: str, style: str) -> Optional[bytes]:
        """
        Generates an image using the Stability AI API.
        """
        try:
            logger.info("Generating image with Stability AI...")
            response = requests.post(
                Config.STABILITY_API_URL,
                headers={"authorization": f"Bearer {Config.STABILITY_API_KEY}", "Accept": "image/*"},
                files={"none": ""},
                data={
                    "prompt": prompt,
                    "style_preset": "cartoon",
                    "output_format": "webp",
                },
            )

            if response.status_code == 200:
                logger.info("Image generated successfully via Stability AI.")
                return response.content
            else:
                logger.error(f"Stability AI API error: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error generating image with Stability AI: {e}")
            return None

    def _generate_with_huggingface(self, prompt: str) -> Optional[bytes]:
        """
        Generates an image using a Hugging Face Inference API endpoint.
        """
        try:
            logger.info("Generating image with Hugging Face...")
            response = requests.post(Config.HUGGINGFACE_API_URL, headers=self.headers, json={"inputs": prompt})
            
            if response.status_code == 200:
                logger.info("Image generated successfully via Hugging Face.")
                return response.content
            else:
                logger.error(f"Hugging Face API error: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error generating image with Hugging Face: {e}")
            return None
    
    def generate_image(self, situation: str, style: str = "meme") -> Optional[bytes]:
        """
        Generates an image, prioritizing local Stable Diffusion, then falling back to APIs.
        The 'situation' directly serves as the prompt for image generation.
        """
        prompt = self._build_image_prompt(situation, style)
        
        # Try local Stable Diffusion first
        image_bytes = self._generate_with_local_sd(prompt)
        if image_bytes:
            return image_bytes

        # Fallback to Stability AI
        image_bytes = self._generate_with_stability_ai(prompt, style)
        if image_bytes:
            return image_bytes
            
        # Fallback to Hugging Face
        image_bytes = self._generate_with_huggingface(prompt)
        if image_bytes:
            return image_bytes
            
        logger.error("Failed to generate image with all available methods.")
        return None

    def generate_complete_meme(self, situation: str, style: str = 'cartoon') -> Optional[str]:
        """
        Orchestrates the process to create and save an image based on the situation and style.
        Caption generation and adding has been removed.
        """
        # Step 1: Generate the image based on the situation and style
        image_bytes = self.generate_image(situation, style)
        if not image_bytes:
            return None

        # Step 2: Save the generated image
        os.makedirs(Config.GENERATED_MEME_DIR, exist_ok=True)
        filename = f"{situation.replace(' ', '_')}.png"
        filepath = os.path.join(Config.GENERATED_MEME_DIR, filename)

        with open(filepath, "wb") as f:
            f.write(image_bytes)
        
        logger.info(f"Image saved successfully at: {filepath}")
        return filepath

# Example usage (for direct script execution)
if __name__ == "__main__":
    generator = MemeGenerator()
    situation = "a majestic cat sitting on a throne"
    generator.generate_complete_meme(situation)
