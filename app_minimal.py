#!/usr/bin/env python3
"""
Minimal Pet Ingredient Safety Checker for DigitalOcean Deployment
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Simple HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pet Ingredient Safety Checker</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f8f9fa; padding: 30px; border-radius: 10px; }
        h1 { color: #2c5aa0; text-align: center; }
        .form-group { margin: 20px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        select, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #2c5aa0; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #1a4480; }
        .results { margin-top: 30px; }
        .high-risk { background: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 10px 0; }
        .medium-risk { background: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; margin: 10px 0; }
        .low-risk { background: #f3e5f5; border-left: 4px solid #9c27b0; padding: 15px; margin: 10px 0; }
        .no-risk { background: #e8f5e8; border-left: 4px solid #4caf50; padding: 15px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐾 Pet Ingredient Safety Checker</h1>
        <p>Check ingredient safety for your pets using our multi-agent system</p>
        
        <div class="form-group">
            <label for="petType">Select your pet:</label>
            <select id="petType">
                <option value="cat">🐱 Cat</option>
                <option value="dog">🐕 Dog</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="ingredients">Enter ingredients (one per line):</label>
            <textarea id="ingredients" rows="6" placeholder="chocolate&#10;onions&#10;chicken&#10;rice"></textarea>
        </div>
        
        <button onclick="evaluateIngredients()">Evaluate Ingredients</button>
        
        <div id="results" class="results"></div>
    </div>

    <script>
        async function evaluateIngredients() {
            const petType = document.getElementById('petType').value;
            const ingredients = document.getElementById('ingredients').value.split('\\n').filter(i => i.trim());
            
            if (ingredients.length === 0) {
                alert('Please enter at least one ingredient');
                return;
            }
            
            try {
                const response = await fetch('/api/evaluate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ingredients, pet_type: petType })
                });
                
                const data = await response.json();
                displayResults(data.results);
            } catch (error) {
                alert('Error evaluating ingredients: ' + error.message);
            }
        }
        
        function displayResults(results) {
            const resultsDiv = document.getElementById('results');
            let html = '<h2>Safety Assessment Results</h2>';
            
            ['high', 'medium', 'low', 'no'].forEach(risk => {
                const items = results[risk] || [];
                if (items.length > 0) {
                    html += `<div class="${risk}-risk">`;
                    html += `<h3>${risk.charAt(0).toUpperCase() + risk.slice(1)} Risk (${items.length} ingredients)</h3>`;
                    items.forEach(item => {
                        html += `<p><strong>${item.name}</strong>: ${item.justification}</p>`;
                        html += `<small>Sources: ${item.sources}</small><br><br>`;
                    });
                    html += '</div>';
                }
            });
            
            resultsDiv.innerHTML = html;
        }
    </script>
</body>
</html>
'''

# Ingredient database
INGREDIENT_DB = {
    'chocolate': {
        'dog': {'risk': 'high', 'details': 'Contains theobromine and caffeine, toxic to dogs'},
        'cat': {'risk': 'high', 'details': 'Contains theobromine and caffeine, toxic to cats'},
        'sources': 'ASPCA Animal Poison Control'
    },
    'onion': {
        'dog': {'risk': 'high', 'details': 'Causes oxidative damage to red blood cells'},
        'cat': {'risk': 'high', 'details': 'Extremely toxic - causes severe anemia'},
        'sources': 'ASPCA Animal Poison Control'
    },
    'chicken': {
        'dog': {'risk': 'no', 'details': 'Safe protein source when properly cooked'},
        'cat': {'risk': 'no', 'details': 'Excellent protein source for cats'},
        'sources': 'AVMA Guidelines'
    },
    'rice': {
        'dog': {'risk': 'no', 'details': 'Easily digestible carbohydrate source'},
        'cat': {'risk': 'no', 'details': 'Safe carbohydrate for cats'},
        'sources': 'AAFCO Guidelines'
    }
}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/evaluate', methods=['POST'])
def evaluate_ingredients():
    try:
        data = request.get_json()
        ingredients = data.get('ingredients', [])
        pet_type = data.get('pet_type', 'cat')
        
        results = {'high': [], 'medium': [], 'low': [], 'no': []}
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower().strip()
            
            # Get ingredient data
            ingredient_data = INGREDIENT_DB.get(ingredient_lower, {
                'dog': {'risk': 'medium', 'details': 'Unknown ingredient - consult veterinarian'},
                'cat': {'risk': 'medium', 'details': 'Unknown ingredient - consult veterinarian'},
                'sources': 'Consult your veterinarian'
            })
            
            pet_data = ingredient_data.get(pet_type, ingredient_data.get('dog', {}))
            risk_level = pet_data.get('risk', 'medium')
            
            # Format result
            result = {
                'name': ingredient,
                'risk_level': risk_level,
                'justification': f"{ingredient.capitalize()} {pet_data.get('details', '')}",
                'sources': ingredient_data.get('sources', 'Veterinary consultation recommended')
            }
            
            results[risk_level].append(result)
        
        return jsonify({
            'success': True,
            'results': results,
            'pet_type': pet_type,
            'processed_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Pet Ingredient Safety Checker is running'
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
