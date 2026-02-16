import cv2
import numpy as np
import random
from PIL import Image, ImageDraw
import os

def are_colors_similar(c1, c2, threshold=20):
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    dist = np.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)
    return dist < threshold

def process_board_input(image_path, grid_size=8):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not load image.")

    target_dim = grid_size * 50 
    img_resized = cv2.resize(img, (target_dim, target_dim), interpolation=cv2.INTER_AREA)
    
    cell_width = target_dim // grid_size
    cell_height = target_dim // grid_size
    
    total_cells = grid_size * grid_size
    region_matrix = ['X'] * total_cells 
    
    known_colors = {}
    region_counter = 1

    sample_ratio = 0.2 
    half_sample_w = max(1, int((cell_width * sample_ratio) / 2))
    half_sample_h = max(1, int((cell_height * sample_ratio) / 2))
    
    for row in range(grid_size):
        for col in range(grid_size):
            flat_index = (row * grid_size) + col
            center_x = (col * cell_width) + (cell_width // 2)
            center_y = (row * cell_height) + (cell_height // 2)
            
            patch = img_resized[
                center_y - half_sample_h : center_y + half_sample_h,
                center_x - half_sample_w : center_x + half_sample_w
            ]
            
            if patch.size == 0:
                pixel_color = tuple(img_resized[center_y, center_x])
            else:
                median_color = np.median(patch.reshape(-1, 3), axis=0)
                pixel_color = tuple(median_color.astype(int))

            found_existing = False
            for existing_color, region_char in known_colors.items():
                if are_colors_similar(pixel_color, existing_color):
                    region_matrix[flat_index] = region_char
                    found_existing = True
                    break
            
            if not found_existing:
                new_char = chr(region_counter + 64)
                known_colors[pixel_color] = new_char
                region_matrix[flat_index] = new_char
                region_counter += 1

    return region_matrix

def create_board_from_text(text_content, grid_size, output_path="temp_text_board.png"):

    clean_text = "".join(text_content.split())
    if len(clean_text) != grid_size * grid_size:
        raise ValueError(f"Text length ({len(clean_text)}) does not match grid size")

    cell_size = 60
    img_size = grid_size * cell_size
    img = Image.new("RGB", (img_size, img_size), "white")
    draw = ImageDraw.Draw(img)

    # Randomize colors
    random.seed(42) 
    color_map = {}
    
    for r in range(grid_size):
        for c in range(grid_size):
            char = clean_text[r * grid_size + c]
            if char not in color_map:
  
                color_map[char] = (
                    random.randint(100, 255),
                    random.randint(100, 255),
                    random.randint(100, 255)
                )
            
            x0 = c * cell_size
            y0 = r * cell_size
            x1 = x0 + cell_size
            y1 = y0 + cell_size
            
            # Draw cell background
            draw.rectangle([x0, y0, x1, y1], fill=color_map[char], outline="black", width=2)

    
    img.save(output_path)
    return output_path, list(clean_text)

def generate_board_output(original_image_path, solution_matrix, output_path="output/solution.png", output_size=8):
    base_image = Image.open(original_image_path).convert("RGBA")
    width, height = base_image.size
    
    cell_w = width / output_size
    cell_h = height / output_size

    try:
        queen_icon = Image.open("queen_asset.png").convert("RGBA")
        icon_size = int(min(cell_w, cell_h) * 0.8) 
        queen_icon = queen_icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
    except FileNotFoundError:
        queen_icon = None

    draw = ImageDraw.Draw(base_image)

    for row in range(output_size):
        for col in range(output_size):
            flat_index = (row * output_size) + col
            if solution_matrix[flat_index] == 1:
                x_pos = int((col * cell_w) + (cell_w / 2))
                y_pos = int((row * cell_h) + (cell_h / 2))

                if queen_icon:
                    offset_x = int(x_pos - (queen_icon.width // 2))
                    offset_y = int(y_pos - (queen_icon.height // 2))
                    base_image.alpha_composite(queen_icon, (offset_x, offset_y))
                else:
                    r = min(cell_w, cell_h) * 0.3
                    draw.ellipse(
                        (x_pos - r, y_pos - r, x_pos + r, y_pos + r), 
                        fill=(255, 0, 0, 255), outline="black"
                    )
    os.makedirs("output", exist_ok=True)
    base_image.save(output_path)
    return output_path