from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
from transformers import FlaxAutoModelForSeq2SeqLM, AutoTokenizer

# Load the YOLO model for ingredient detection
model_yolo = YOLO(r'best.pt')

# Input image path
input_image_path = r'C:\Users\Admin\Downloads\Smart Recipe Generation\Veg3.webp'
# Perform prediction to detect ingredients
results = model_yolo(input_image_path)

# Extract detected ingredients from YOLO results
detected_boxes = results[0].boxes
class_indices = detected_boxes.cls.cpu().numpy().astype(int)
ingredient_names = [model_yolo.names[idx] for idx in class_indices]
ingredients_str = ", ".join(set(ingredient_names))  # Use set to remove duplicates

print("Detected Ingredients:", ingredients_str)

# Load recipe generation model and tokenizer
MODEL_NAME_OR_PATH = "flax-community/t5-recipe-generation"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME_OR_PATH, use_fast=True)
model_recipe = FlaxAutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME_OR_PATH)

# Define generation parameters (removed no_repeat_ngram_size)
generation_kwargs = {
    "max_length": 512,
    "min_length": 64,
    "do_sample": True,
    "top_k": 60,
    "top_p": 0.95
}

special_tokens = tokenizer.all_special_tokens
tokens_map = {
    "<sep>": "--",
    "<section>": "\n"
}

def skip_special_tokens(text, special_tokens):
    for token in special_tokens:
        text = text.replace(token, "")
    return text

def target_postprocessing(texts, special_tokens):
    if not isinstance(texts, list):
        texts = [texts]
    new_texts = []
    for text in texts:
        text = skip_special_tokens(text, special_tokens)
        for k, v in tokens_map.items():
            text = text.replace(k, v)
        new_texts.append(text)
    return new_texts

def generate_recipe(texts):
    _inputs = texts if isinstance(texts, list) else [texts]
    inputs = ["items: " + inp for inp in _inputs]
    inputs = tokenizer(
        inputs,
        max_length=256,
        padding="max_length",
        truncation=True,
        return_tensors="jax"
    )
    output_ids = model_recipe.generate(
        input_ids=inputs.input_ids,
        attention_mask=inputs.attention_mask,
        **generation_kwargs
    )
    generated_recipe = target_postprocessing(
        tokenizer.batch_decode(output_ids.sequences, skip_special_tokens=False),
        special_tokens
    )
    return generated_recipe

# Generate recipe using detected ingredients
if ingredient_names:
    generated_recipes = generate_recipe([ingredients_str])
    
    # Print the generated recipe
    for text in generated_recipes:
        sections = text.split("\n")
        headline = ""
        for section in sections:
            section = section.strip()
            if section.startswith("title:"):
                section = section.replace("title:", "")
                headline = "TITLE"
            elif section.startswith("ingredients:"):
                section = section.replace("ingredients:", "")
                headline = "INGREDIENTS"
            elif section.startswith("directions:"):
                section = section.replace("directions:", "")
                headline = "DIRECTIONS"

            if not section:
                continue

            if headline == "TITLE":
                print(f"[{headline}]: {section.strip().capitalize()}")
            else:
                print(f"[{headline}]:")
                parts = section.split("--")
                for i, part in enumerate(parts, 1):
                    part = part.strip()
                    if part:
                        print(f"  - {i}: {part.capitalize()}")
        print("-" * 130)
else:
    print("No ingredients detected. Cannot generate recipe.")

# Retrieve the processed image with detections
detected_image = results[0].plot()  # Draw bounding boxes and labels on the image

# Convert the image to RGB for displaying with Matplotlib
detected_image_rgb = cv2.cvtColor(detected_image, cv2.COLOR_BGR2RGB)

# Display the detected image
plt.imshow(detected_image_rgb)
plt.axis("off")  # Turn off axis labels
plt.show()

# Save the output image (optional)
# output_image_path = r'C:\Users\Admin\Downloads\Smart Recipe Generation\detected_image.jpg'
# cv2.imwrite(output_image_path, detected_image)
# print(f"Detected image saved to {output_image_path}")