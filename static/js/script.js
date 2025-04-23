let ingredients = [];
let stream = null;

document.addEventListener('DOMContentLoaded', () => {
    AOS.init({ duration: 800, once: true });

    // Image upload handling
    document.getElementById('imageUpload').addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                document.getElementById('imagePreview').src = e.target.result;
                document.getElementById('imagePreview').classList.remove('d-none');
                document.getElementById('noPreview').classList.add('d-none');
            };
            reader.readAsDataURL(file);
        }
    });

    // Detect ingredients from image
    document.getElementById('detectBtn').addEventListener('click', async () => {
        const fileInput = document.getElementById('imageUpload');
        if (!fileInput.files[0]) {
            alert('Please select an image first');
            return;
        }

        showLoading();
        const formData = new FormData();
        formData.append('image', fileInput.files[0]);

        try {
            const response = await fetch('/detect', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (data.ingredients && data.ingredients !== "No ingredients detected") {
                data.ingredients.split(', ').forEach(ing => {
                    if (!ingredients.includes(ing)) {
                        ingredients.push(ing);
                    }
                });
                updateIngredientList();
            } else {
                alert('No ingredients detected in the image');
            }
        } catch (error) {
            alert('Error detecting ingredients: ' + error.message);
        } finally {
            hideLoading();
        }
    });

    // Camera handling
    document.getElementById('cameraBtn').addEventListener('click', async () => {
        const video = document.getElementById('video');
        const captureBtn = document.getElementById('captureBtn');
        
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            video.classList.remove('d-none');
            captureBtn.classList.remove('d-none');
        } catch (error) {
            alert('Error accessing camera: ' + error.message);
        }
    });

    document.getElementById('captureBtn').addEventListener('click', async () => {
        const video = document.getElementById('video');
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        
        showLoading();
        const blob = await new Promise(resolve => canvas.toBlob(resolve));
        const formData = new FormData();
        formData.append('image', blob, 'capture.jpg');

        try {
            const response = await fetch('/detect', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (data.ingredients && data.ingredients !== "No ingredients detected") {
                data.ingredients.split(', ').forEach(ing => {
                    if (!ingredients.includes(ing)) {
                        ingredients.push(ing);
                    }
                });
                updateIngredientList();
            } else {
                alert('No ingredients detected in the capture');
            }
        } catch (error) {
            alert('Error detecting ingredients: ' + error.message);
        } finally {
            hideLoading();
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                video.classList.add('d-none');
                document.getElementById('captureBtn').classList.add('d-none');
            }
        }
    });

    // Add manual ingredient
    document.getElementById('addBtn').addEventListener('click', addIngredient);
    document.getElementById('ingredientInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addIngredient();
    });

    // Generate recipe
    document.getElementById('generateBtn').addEventListener('click', generateRecipe);

    // Smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelector(anchor.getAttribute('href')).scrollIntoView({ behavior: 'smooth' });
        });
    });
});

function addIngredient() {
    const input = document.getElementById('ingredientInput');
    const ingredient = input.value.trim();
    if (ingredient && !ingredients.includes(ingredient)) {
        ingredients.push(ingredient);
        updateIngredientList();
        input.value = '';
    }
}

function updateIngredientList() {
    const list = document.getElementById('ingredientList');
    const generateBtn = document.getElementById('generateBtn');
    list.innerHTML = '';

    ingredients.forEach((ing, index) => {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.innerHTML = `
            ${ing}
            <button class="remove-btn" onclick="removeIngredient(${index})">
                <i class="fas fa-times"></i>
            </button>
        `;
        list.appendChild(li);
    });

    generateBtn.disabled = ingredients.length === 0;
}

function removeIngredient(index) {
    ingredients.splice(index, 1);
    updateIngredientList();
}

async function generateRecipe() {
    if (ingredients.length === 0) {
        alert('Please add some ingredients first');
        return;
    }

    showLoading();
    const content = document.getElementById('recipeContent');
    const noRecipe = document.getElementById('noRecipe');

    content.classList.add('d-none');
    noRecipe.classList.add('d-none');

    try {
        const response = await fetch('/recipe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ingredients: ingredients.join(', ') })
        });
        const data = await response.json();

        if (data.recipe) {
            content.innerHTML = formatRecipe(data.recipe);
            content.classList.remove('d-none');
            document.getElementById('recipe').scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        alert('Error generating recipe: ' + error.message);
        noRecipe.classList.remove('d-none');
    } finally {
        hideLoading();
    }
}

function formatRecipe(recipe) {
    const lines = recipe.split('\n');
    let html = '';
    
    lines.forEach(line => {
        if (line.startsWith('[TITLE]')) {
            html += `<h3 class="recipe-title">${line.replace('[TITLE]:', '').trim()}</h3>`;
        } else if (line.startsWith('[DIRECTIONS]')) {
            html += '<h5>Directions</h5><ol class="list-group list-group-numbered">';
        } else if (line.trim() !== '' && !line.startsWith('[TITLE]') && !line.startsWith('[DIRECTIONS]')) {
            // Remove the "- " prefix and trim the step
            const step = line.replace(/^\s*-\s*/, '').trim();
            html += `<li class="list-group-item">${step}</li>`;
        } else if (line.trim() === '') {
            html += '</ol>';
        }
    });
    
    return html;
}

function showLoading() {
    document.getElementById('loading').classList.remove('d-none');
}

function hideLoading() {
    document.getElementById('loading').classList.add('d-none');
}