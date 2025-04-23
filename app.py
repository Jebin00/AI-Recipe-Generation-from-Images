from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import cv2
from ultralytics import YOLO
from transformers import FlaxAutoModelForSeq2SeqLM, AutoTokenizer
import tempfile
import os
import logging
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

BASE_DIR = Path(__file__).parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

try:
    model_yolo = YOLO('best.pt')
    tokenizer = AutoTokenizer.from_pretrained("flax-community/t5-recipe-generation")
    model_recipe = FlaxAutoModelForSeq2SeqLM.from_pretrained("flax-community/t5-recipe-generation")
except Exception as e:
    logger.error(f"Model loading failed: {str(e)}")
    raise

generation_kwargs = {
    "max_length": 512,
    "min_length": 64,
    "do_sample": True,
    "top_k": 60,
    "top_p": 0.95
}

# generation_kwargs = {
#     "max_length": 1024,
#     "min_length": 64,
#     "do_sample": True,
#     # "top_k": 60,
#     # "top_p": 0.95,
# }

def generate_recipe(text):
    inputs = tokenizer([f"items: {text}"], return_tensors="jax", padding=True, truncation=True)
    output = model_recipe.generate(**inputs, **generation_kwargs)
    decoded = tokenizer.decode(output.sequences[0], skip_special_tokens=False)
    if "title:" not in decoded or "directions:" not in decoded:
        title = f"Custom Recipe with {text.split(',')[0]}"
        directions = decoded.replace('<section>', '\n').replace('<sep>', '\n')
        return f"[TITLE]: {title}\n[DIRECTIONS]:\n{directions}"
    return decoded.replace('<section>', '\n').replace('<sep>', '\n')

def format_recipe(text, ingredients):
    formatted = []
    sections = text.split('\n')
    title_added = False
    directions_started = False
    
    for section in sections:
        section = section.strip()
        if section.startswith('title:') and not title_added:
            formatted.append(f"[TITLE]: {section.replace('title:', '').capitalize()}")
            title_added = True
        elif section.startswith('directions:'):
            formatted.append("[DIRECTIONS]:")
            directions_started = True
        elif directions_started and section:
            step = re.sub(r'^\s*-\s*', '', section).strip()
            formatted.append(step)
    
    if not title_added:
        formatted.insert(0, f"[TITLE]: Custom {ingredients.split(',')[0].capitalize()} Dish")
    
    return "\n".join(formatted)

@app.get("/")
async def root(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return JSONResponse({"error": "Internal Server Error"}, status_code=500)

@app.post("/detect")
async def detect(image: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(await image.read())
            tmp_path = tmp.name

        img = cv2.imread(tmp_path)
        results = model_yolo(img)
        ingredients = set()
        
        if results and results[0].boxes is not None and len(results[0].boxes) > 0:
            for cls in results[0].boxes.cls:
                class_name = model_yolo.names[int(cls)].capitalize()
                ingredients.add(class_name)
        else:
            logger.info("No objects detected in the image")
        
        os.unlink(tmp_path)
        return {"ingredients": ", ".join(ingredients) if ingredients else "No ingredients detected"}
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/recipe")
async def create_recipe(request: Request):
    try:
        data = await request.json()
        ingredients = data.get("ingredients", "")
        if not ingredients:
            return JSONResponse({"error": "No ingredients provided"}, status_code=400)
        
        recipe = generate_recipe(ingredients)
        formatted = format_recipe(recipe, ingredients)
        return {"recipe": formatted}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)