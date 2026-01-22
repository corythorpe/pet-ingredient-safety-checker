#!/usr/bin/env python3
"""
Pet Ingredient Safety Checker - Simplified Deployment Version
Multi-agent system for DigitalOcean deployment
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Comprehensive ingredient knowledge base with specific URLs
INGREDIENT_DATABASE = {
    'chocolate': {
        'dog': {'risk': 'high', 'details': 'Contains theobromine and caffeine, which dogs cannot metabolize effectively'},
        'cat': {'risk': 'high', 'details': 'Contains theobromine and caffeine, highly toxic to cats'},
        'sources': 'ASPCA (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/chocolate), Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/chocolate/)',
        'symptoms': 'vomiting, diarrhea, seizures, cardiac arrhythmias, death',
        'mechanism': 'Theobromine toxicity affecting cardiovascular and nervous systems'
    },
    'onion': {
        'dog': {'risk': 'high', 'details': 'Contains N-propyl disulfide causing oxidative damage to red blood cells'},
        'cat': {'risk': 'high', 'details': 'Extremely toxic - causes severe hemolytic anemia'},
        'sources': 'ASPCA (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/onion), VCA Animal Hospitals (https://vcahospitals.com/know-your-pet/onion-garlic-chive-and-leek-toxicity-in-dogs)',
        'symptoms': 'anemia, weakness, pale gums, difficulty breathing',
        'mechanism': 'Oxidative damage to red blood cells leading to hemolytic anemia'
    },
    'garlic': {
        'dog': {'risk': 'high', 'details': 'More potent than onions - causes severe oxidative damage'},
        'cat': {'risk': 'high', 'details': 'Highly toxic - more dangerous than onions for cats'},
        'sources': 'ASPCA (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/garlic), Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/garlic/)',
        'symptoms': 'anemia, weakness, collapse, organ damage',
        'mechanism': 'Allicin and other sulfur compounds cause oxidative red blood cell damage'
    },
    'grapes': {
        'dog': {'risk': 'high', 'details': 'Unknown toxic compound causes acute kidney failure'},
        'cat': {'risk': 'medium', 'details': 'Less documented in cats but potentially nephrotoxic'},
        'sources': 'ASPCA (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/grape), FDA (https://www.fda.gov/animal-veterinary/animal-health-literacy/dangers-grapes-and-raisins-dogs)',
        'symptoms': 'vomiting, kidney failure, death',
        'mechanism': 'Unknown nephrotoxic compound causing acute renal failure'
    },
    'raisins': {
        'dog': {'risk': 'high', 'details': 'Concentrated grape toxicity - even small amounts dangerous'},
        'cat': {'risk': 'medium', 'details': 'Potentially nephrotoxic like grapes'},
        'sources': 'Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/raisin/), ASPCA (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/grape)',
        'symptoms': 'kidney failure, vomiting, lethargy',
        'mechanism': 'Concentrated nephrotoxic compounds from grapes'
    },
    'ibuprofen': {
        'dog': {'risk': 'high', 'details': 'NSAIDs are extremely dangerous - can cause kidney failure, liver damage, and death'},
        'cat': {'risk': 'high', 'details': 'Highly toxic - cats cannot metabolize NSAIDs, leading to severe organ damage'},
        'sources': 'ASPCA (https://www.aspca.org/pet-care/animal-poison-control/people-foods-avoid-feeding-your-pets), Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/ibuprofen/), VCA Animal Hospitals (https://vcahospitals.com/know-your-pet/ibuprofen-toxicity-in-dogs-and-cats)',
        'symptoms': 'vomiting, diarrhea, loss of appetite, kidney failure, liver damage, seizures, coma, death',
        'mechanism': 'Inhibits cyclooxygenase enzymes causing gastrointestinal ulceration and renal toxicity'
    },
    'acetaminophen': {
        'dog': {'risk': 'high', 'details': 'Causes liver damage and methemoglobinemia - potentially fatal'},
        'cat': {'risk': 'high', 'details': 'Extremely toxic - cats lack glucuronidation enzymes, making acetaminophen lethal'},
        'sources': 'ASPCA (https://www.aspca.org/pet-care/animal-poison-control/people-foods-avoid-feeding-your-pets), Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/acetaminophen/), VCA Animal Hospitals (https://vcahospitals.com/know-your-pet/acetaminophen-toxicity-in-cats)',
        'symptoms': 'difficulty breathing, brown gums, liver failure, swelling of face and paws, death',
        'mechanism': 'Depletes glutathione causing hepatotoxicity and methemoglobinemia'
    },
    'xylitol': {
        'dog': {'risk': 'high', 'details': 'Causes rapid insulin release leading to severe hypoglycemia and liver failure'},
        'cat': {'risk': 'medium', 'details': 'Less sensitive than dogs but still potentially dangerous'},
        'sources': 'FDA (https://www.fda.gov/consumers/consumer-updates/paws-xylitol-its-dangerous-dogs), ASPCA (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/xylitol), Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/xylitol/)',
        'symptoms': 'vomiting, loss of coordination, lethargy, collapse, seizures, liver failure',
        'mechanism': 'Rapid insulin release causing hypoglycemia and hepatic necrosis'
    },
    'caffeine': {
        'dog': {'risk': 'high', 'details': 'Methylxanthine toxicity similar to chocolate but more concentrated'},
        'cat': {'risk': 'high', 'details': 'Highly toxic - cats are very sensitive to methylxanthines'},
        'sources': 'ASPCA (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/coffee), Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/caffeine/), VCA Animal Hospitals (https://vcahospitals.com/know-your-pet/caffeine-toxicity-in-pets)',
        'symptoms': 'restlessness, rapid breathing, heart palpitations, muscle tremors, seizures',
        'mechanism': 'Methylxanthine toxicity affecting cardiovascular and nervous systems'
    },
    'chicken': {
        'dog': {'risk': 'no', 'details': 'Safe protein source when properly cooked'},
        'cat': {'risk': 'no', 'details': 'Excellent protein source for cats'},
        'sources': 'AVMA (https://www.avma.org/resources-tools/pet-owners/petcare/selecting-nutritious-pet-food), AAFCO (https://www.aafco.org/consumers/understanding-pet-food)',
        'symptoms': 'none when properly prepared',
        'mechanism': 'High-quality protein with essential amino acids'
    },
    'rice': {
        'dog': {'risk': 'no', 'details': 'Easily digestible carbohydrate source'},
        'cat': {'risk': 'no', 'details': 'Safe carbohydrate, though cats have limited carbohydrate needs'},
        'sources': 'AAFCO (https://www.aafco.org/consumers/understanding-pet-food), VCA Animal Hospitals (https://vcahospitals.com/know-your-pet/dog-feeding-guide)',
        'symptoms': 'none',
        'mechanism': 'Provides digestible carbohydrates and energy'
    },
    'avocado': {
        'dog': {'risk': 'medium', 'details': 'Contains persin, which can cause digestive upset'},
        'cat': {'risk': 'medium', 'details': 'Persin toxicity can cause digestive and cardiac issues'},
        'sources': 'ASPCA (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/avocado), Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/avocado/)',
        'symptoms': 'vomiting, diarrhea, difficulty breathing',
        'mechanism': 'Persin compound causes gastrointestinal and cardiac effects'
    }
}

class MultiAgentSystem:
    """Simulated multi-agent system for ingredient analysis"""
    
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.risk_analysis_agent = RiskAnalysisAgent()
        self.fact_checker_agent = FactCheckerAgent()
        self.formatter_agent = FormatterAgent()
    
    def process_ingredients(self, ingredients, pet_type, category):
        """Process ingredients through the multi-agent pipeline"""
        logger.info(f"🤖 Multi-Agent System: Processing {len(ingredients)} ingredients for {pet_type} ({category})")
        
        results = {'high': [], 'medium': [], 'low': [], 'no': []}
        
        for ingredient in ingredients:
            try:
                # Research Agent: Gather information
                logger.info(f"🔍 Research Agent: Researching {ingredient}")
                research_data = self.research_agent.research(ingredient, pet_type, category)
                
                # Risk Analysis Agent: Categorize risk
                logger.info(f"⚖️ Risk Analysis Agent: Analyzing {ingredient}")
                risk_level = self.risk_analysis_agent.analyze(research_data)
                
                # Fact Checker Agent: Validate findings
                logger.info(f"✅ Fact Checker Agent: Validating {ingredient}")
                validated_data = self.fact_checker_agent.validate(research_data, risk_level)
                
                # Formatter Agent: Structure output
                logger.info(f"📝 Formatter Agent: Formatting {ingredient}")
                formatted_result = self.formatter_agent.format(ingredient, validated_data, risk_level)
                
                results[risk_level].append(formatted_result)
                
            except Exception as e:
                logger.error(f"Error processing {ingredient}: {e}")
                results['medium'].append({
                    'name': ingredient,
                    'risk_level': 'medium',
                    'justification': f"Error occurred while researching {ingredient}. Consult your veterinarian.",
                    'sources': 'ASPCA Animal Poison Control (https://www.aspca.org/pet-care/animal-poison-control)',
                    'cached': False
                })
        
        return results

class ResearchAgent:
    def research(self, ingredient, pet_type, category):
        data = INGREDIENT_DATABASE.get(ingredient.lower(), {
            'dog': {'risk': 'unknown', 'details': 'Insufficient data available'},
            'cat': {'risk': 'unknown', 'details': 'Insufficient data available'},
            'sources': 'For unknown ingredients, consult ASPCA Animal Poison Control (https://www.aspca.org/pet-care/animal-poison-control)',
            'symptoms': 'unknown - monitor for changes in behavior',
            'mechanism': 'requires veterinary assessment'
        })
        
        return {
            'ingredient': ingredient,
            'pet_type': pet_type,
            'pet_data': data.get(pet_type, data.get('dog', {})),
            'sources': data.get('sources', ''),
            'symptoms': data.get('symptoms', ''),
            'mechanism': data.get('mechanism', ''),
            'cached': False
        }

class RiskAnalysisAgent:
    def analyze(self, research_data):
        risk = research_data['pet_data'].get('risk', 'unknown')
        return 'medium' if risk == 'unknown' else risk

class FactCheckerAgent:
    def validate(self, research_data, risk_level):
        research_data['validated'] = True
        research_data['final_risk_level'] = risk_level
        return research_data

class FormatterAgent:
    def format(self, ingredient, validated_data, risk_level):
        pet_type = validated_data['pet_type']
        pet_data = validated_data['pet_data']
        
        if risk_level == 'no':
            justification = f"{ingredient.capitalize()} is generally safe for {pet_type}s. {pet_data.get('details', '')}"
        else:
            risk_descriptions = {
                'high': 'poses a serious threat and can be life-threatening',
                'medium': 'can cause significant health problems',
                'low': 'may cause mild adverse reactions'
            }
            justification = f"{ingredient.capitalize()} {risk_descriptions.get(risk_level, 'requires caution')} for {pet_type}s. {pet_data.get('details', '')}"
            
            if validated_data.get('symptoms') and validated_data['symptoms'] != 'none':
                justification += f" Symptoms may include: {validated_data['symptoms']}."
            
            if validated_data.get('mechanism') and 'requires' not in validated_data['mechanism']:
                justification += f" Mechanism: {validated_data['mechanism']}."
        
        return {
            'name': ingredient,
            'risk_level': risk_level,
            'justification': justification,
            'sources': validated_data.get('sources', ''),
            'cached': validated_data.get('cached', False)
        }

# Initialize multi-agent system
agents = MultiAgentSystem()

@app.route('/')
def index():
    """Serve the main application"""
    return render_template('index.html')

@app.route('/api/evaluate', methods=['POST'])
def evaluate_ingredients():
    """API endpoint to evaluate ingredients using multi-agent system"""
    try:
        data = request.get_json()
        
        if not data or 'ingredients' not in data:
            return jsonify({'error': 'Missing ingredients'}), 400
        
        ingredients = data['ingredients']
        pet_type = data.get('pet_type', 'cat')
        category = data.get('category', 'mixed')
        
        if not ingredients:
            return jsonify({'error': 'No ingredients provided'}), 400
        
        logger.info(f"🚀 Processing request: {len(ingredients)} ingredients for {pet_type}")
        
        # Process through multi-agent system
        results = agents.process_ingredients(ingredients, pet_type, category)
        
        return jsonify({
            'success': True,
            'results': results,
            'pet_type': pet_type,
            'category': category,
            'processed_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in evaluate_ingredients: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'agents': {
            'research_agent': 'active',
            'risk_analysis_agent': 'active',
            'fact_checker_agent': 'active',
            'formatter_agent': 'active'
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"🐾 Starting Pet Ingredient Safety Checker on port {port}")
    logger.info("🤖 Multi-Agent System initialized and ready")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
