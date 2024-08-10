import os
import numpy as np
from PIL import Image, ImageOps
import logging

def generate_roughness_maps(directory, texture_format, darkness_value):
    darkness_factor = 255 - int(darkness_value)

    for root, _, files in os.walk(directory):
        for file_name in files:
            if (file_name.lower().endswith(texture_format) and
                    '_normal' not in file_name.lower() and
                    '_noalpha' not in file_name.lower() and
                    '_roughness' not in file_name.lower() and
                    '_selfillum' not in file_name.lower() and
                    '_color' not in file_name.lower() and
                    '-ssbump' not in file_name.lower() and
                    '_detail' not in file_name.lower()):
                texture_path = os.path.join(root, file_name)

                try:
                    with Image.open(texture_path) as img:
                        # Convert image to grayscale
                        grayscale_img = ImageOps.grayscale(img)

                        # Check if the surface should be shiny
                        roughness_img = ImageOps.invert(grayscale_img)
                        roughness_img = Image.eval(roughness_img, lambda x: min(255, int(x * darkness_factor / 255)))

                        # Save roughness map
                        base_name, _ = os.path.splitext(file_name)
                        roughness_file_name = f"{base_name}_roughness.{texture_format}"
                        roughness_file_path = os.path.join(root, roughness_file_name)

                        roughness_img.save(roughness_file_path)
                        logging.info(f"Generated roughness map: {roughness_file_path}")

                except Exception as e:
                    logging.error(f"Error processing {file_name}: {e}")

def adjust_roughness_for_shiny_surfaces(directory, texture_format):
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.lower().endswith(f"_roughness.{texture_format}"):
                roughness_path = os.path.join(root, file_name)

                try:
                    with Image.open(roughness_path) as img:
                        img_array = np.array(img)
                        # Make surfaces that are nearly black (high roughness) more prominent
                        shiny_mask = img_array < 30  # Adjust threshold as needed for shiny surfaces
                        img_array[shiny_mask] = 0  # Set shiny areas to zero roughness

                        shiny_img = Image.fromarray(img_array)
                        shiny_img.save(roughness_path)
                        logging.info(f"Adjusted roughness map for shiny surfaces: {roughness_path}")

                except Exception as e:
                    logging.error(f"Error adjusting roughness map {file_name}: {e}")
