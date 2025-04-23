# 🧠 AI-Powered Recipe Generator 🍽️

A FastAPI-based web application that detects ingredients from an uploaded image using YOLOv8 and generates a recipe using a pre-trained NLP model (`flax-community/t5-recipe-generation`).


## 🚀 Features

- Upload or capture an image to detect ingredients
- Manually add ingredients
- AI-generated recipes using deep learning
- Stylish and interactive front-end


## 🛠️ Tech Stack

- **Backend:** FastAPI, Ultralytics YOLOv8, Hugging Face Transformers
- **Frontend:** HTML, CSS, JavaScript
- **Model:** `best.pt` for object detection, `t5-recipe-generation` for NLP
  (https://drive.google.com/file/d/1RFNoyGGBSDIRi69-wT9jwr6b-lQxHsxm/view?usp=sharing) - You can download the weights (best.pt) from this drive link.
  

## 📦 Setup Instructions

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # on Windows use `venv\Scripts\activate`
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Place your `best.pt` YOLO model in the root directory.

5. Run the app:
    ```bash
    uvicorn main:app --reload
    ```

6. Open [http://localhost:8000](http://localhost:8080) in your browser.

   
## 📁 Project Structure

AI Recipe Generation from Visual Inputs/
├── app.py
├── main.py
├── requirements.txt
├── Veg3.webp
├── static/
│   ├── css/
│   │   └── style.css
│   └── jss/
│       └── script.js
└── templates/
    └── index.html


## 🤖 Models Used

- **YOLOv8 (`best.pt`)**: Detects vegetables and fruits from images.
- **T5 Recipe Generator**: Generates cooking instructions based on detected or manually entered ingredients.


## 📸 Screenshots

![Screenshot 2025-04-04 122612](https://github.com/user-attachments/assets/acaee353-80e0-4c4a-895c-e6e06dd5dc45)
![Screenshot 2025-04-04 123519](https://github.com/user-attachments/assets/ba0648eb-4b07-4d40-8e69-50357367dde5)
![Screenshot 2025-04-14 125201](https://github.com/user-attachments/assets/4d8aa13d-e9ad-4883-90a6-c7eb3568c2d3)


## 🙌 Credits

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [Flax T5 Recipe Generator](https://huggingface.co/flax-community/t5-recipe-generation)


## 📝 License

This project is licensed under the MIT License.


