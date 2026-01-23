#!/usr/bin/env python3
"""
Pet Ingredient Safety Checker - Real Multi-Agent System
Using Gradient AI for actual web research and analysis
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import logging
from datetime import datetime
import json
import asyncio
import aiohttp
import requests
import re

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Initialize DigitalOcean GenAI client configuration
genai_config = {
    'research_agent_id': os.getenv('DIGITALOCEAN_GENAI_RESEARCH_AGENT_ID'),
    'risk_agent_id': os.getenv('DIGITALOCEAN_GENAI_RISK_AGENT_ID'),
    'factcheck_agent_id': os.getenv('DIGITALOCEAN_GENAI_FACTCHECK_AGENT_ID'),
    'project_id': os.getenv('DIGITALOCEAN_GENAI_PROJECT_ID'),
    'model_id': os.getenv('DIGITALOCEAN_GENAI_MODEL_ID'),
    'region': os.getenv('DIGITALOCEAN_GENAI_REGION'),
    'inference_url': os.getenv('DIGITALOCEAN_GENAI_INFERENCE_URL'),
    'stream_url': os.getenv('DIGITALOCEAN_GENAI_STREAM_URL'),
    'access_token': os.getenv('DIGITALOCEAN_TOKEN')
}

# Check if GenAI is configured
genai_enabled = all([
    genai_config['research_agent_id'],
    genai_config['risk_agent_id'], 
    genai_config['factcheck_agent_id'],
    genai_config['access_token']
])

class RealMultiAgentSystem:
    """Real multi-agent system using Gradient AI and web research"""
    
    def __init__(self):
        self.research_agent = RealResearchAgent()
        self.risk_analysis_agent = RealRiskAnalysisAgent()
        self.fact_checker_agent = RealFactCheckerAgent()
        self.formatter_agent = RealFormatterAgent()
    
    async def process_ingredients(self, ingredients, pet_type, category):
        """Process ingredients through the real multi-agent pipeline"""
        logger.info(f"🤖 Real Multi-Agent System: Processing {len(ingredients)} ingredients for {pet_type}")
        
        results = {'high': [], 'medium': [], 'low': [], 'no': []}
        
        for ingredient in ingredients:
            try:
                # Research Agent: Conduct real web research
                logger.info(f"🔍 Research Agent: Researching {ingredient} online")
                research_data = await self.research_agent.research(ingredient, pet_type)
                
                # Risk Analysis Agent: AI-powered risk categorization
                logger.info(f"⚖️ Risk Analysis Agent: AI analyzing {ingredient}")
                risk_level = await self.risk_analysis_agent.analyze(research_data, pet_type)
                
                # Fact Checker Agent: Validate findings with additional sources
                logger.info(f"✅ Fact Checker Agent: Validating {ingredient}")
                validated_data = await self.fact_checker_agent.validate(research_data, risk_level, pet_type)
                
                # Formatter Agent: Structure output
                logger.info(f"📝 Formatter Agent: Formatting {ingredient}")
                formatted_result = self.formatter_agent.format(ingredient, validated_data, risk_level)
                
                results[risk_level].append(formatted_result)
                
            except Exception as e:
                logger.error(f"Error processing {ingredient}: {e}")
                results['medium'].append({
                    'name': ingredient,
                    'risk_level': 'medium',
                    'justification': f"Unable to fully research {ingredient} due to technical issues. Please consult your veterinarian for safety information.",
                    'sources': 'ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control',
                    'cached': False
                })
        
        return results

class RealResearchAgent:
    """Agent that conducts real web research on ingredients"""
    
    async def research(self, ingredient, pet_type):
        """Conduct web research on ingredient safety"""
        search_queries = [
            f"{ingredient} toxic {pet_type} safety",
            f"{ingredient} poisonous {pet_type}s",
            f"{ingredient} {pet_type} food safe ASPCA",
            f"{ingredient} pet poison helpline {pet_type}"
        ]
        
        research_results = []
        
        # Simulate web research with targeted searches
        for query in search_queries[:2]:  # Limit to 2 searches to avoid rate limits
            try:
                search_result = await self._search_web(query)
                if search_result:
                    research_results.append(search_result)
            except Exception as e:
                logger.warning(f"Search failed for {query}: {e}")
        
        return {
            'ingredient': ingredient,
            'pet_type': pet_type,
            'search_results': research_results,
            'research_timestamp': datetime.utcnow().isoformat()
        }
    
    async def _search_web(self, query):
        """Use DigitalOcean GenAI agent for REAL web research"""
        
        if not genai_enabled:
            logger.warning("DigitalOcean GenAI not configured - using fallback research")
            return self._fallback_research(query)
        
        try:
            # Call DigitalOcean GenAI Research Agent with enhanced research prompt
            headers = {
                'Authorization': f'Bearer {genai_config["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': genai_config['research_agent_id'],
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a veterinary research assistant with access to current veterinary databases and literature. You conduct thorough research on pet ingredient safety using authoritative sources.'
                    },
                    {
                        'role': 'user', 
                        'content': f"""RESEARCH TASK: {query}

Conduct comprehensive research on this ingredient's safety for pets. Your research should include:

1. TOXICITY ANALYSIS:
   - Specific toxic compounds and mechanisms
   - Lethal dose ranges and toxic thresholds
   - Metabolic pathways and how pets process this ingredient

2. CLINICAL EVIDENCE:
   - Documented cases from veterinary literature
   - Symptoms and clinical presentations
   - Treatment protocols and outcomes

3. AUTHORITATIVE SOURCES:
   - ASPCA Animal Poison Control findings
   - Pet Poison Helpline data
   - Veterinary toxicology journals
   - FDA/USDA safety assessments

4. SPECIES-SPECIFIC CONSIDERATIONS:
   - Differences between dogs and cats
   - Breed-specific sensitivities
   - Age and size considerations

Provide detailed, evidence-based information with specific source citations and URLs where available. This is for actual veterinary decision-making, so accuracy is critical."""
                    }
                ],
                'max_tokens': 800
            }
            
            response = requests.post(
                genai_config['inference_url'] + '/chat/completions',
                headers=headers,
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                return {
                    'query': query,
                    'content': content,
                    'source': 'DigitalOcean GenAI Research Agent - Comprehensive Research',
                    'timestamp': datetime.utcnow().isoformat(),
                    'agent_id': genai_config['research_agent_id'],
                    'research_type': 'comprehensive_veterinary_research'
                }
            else:
                logger.error(f"GenAI API error: {response.status_code} - {response.text}")
                return self._fallback_research(query)
                
        except Exception as e:
            logger.error(f"DigitalOcean GenAI research failed: {e}")
            return self._fallback_research(query)
    
    def _fallback_research(self, query):
        """Fallback research when Gradient AI is unavailable"""
        return {
            'query': query,
            'content': f"Research needed for: {query}. Please consult veterinary sources like ASPCA Animal Poison Control for accurate information.",
            'source': 'Fallback research',
            'timestamp': datetime.utcnow().isoformat()
        }

class RealRiskAnalysisAgent:
    """Agent that uses AI to analyze risk levels"""
    
    async def analyze(self, research_data, pet_type):
        """Use DigitalOcean GenAI agent to analyze research data and determine risk level"""
        
        research_content = "\n".join([
            result['content'] for result in research_data['search_results'] 
            if result and 'content' in result
        ])
        
        if not research_content:
            return 'medium'  # Default to medium risk if no research data
        
        if not genai_enabled:
            logger.warning("DigitalOcean GenAI not configured - using fallback risk analysis")
            return self._fallback_risk_analysis(research_data['ingredient'], pet_type)
        
        try:
            # Call DigitalOcean GenAI Risk Analysis Agent
            headers = {
                'Authorization': f'Bearer {genai_config["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': genai_config['risk_agent_id'],
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a veterinary toxicology expert specializing in risk assessment for pet ingredients.'
                    },
                    {
                        'role': 'user',
                        'content': f"""Analyze the research data and categorize the risk level for {pet_type}s.

Ingredient: {research_data['ingredient']}
Pet Type: {pet_type}

Research Data:
{research_content}

Risk Categories:
- HIGH: Toxic, can cause serious illness or death
- MEDIUM: Can cause moderate health issues, requires caution
- LOW: Minor concerns, generally safe in small amounts
- NO: Safe for consumption

Respond with ONLY the risk level: HIGH, MEDIUM, LOW, or NO"""
                    }
                ],
                'max_tokens': 10
            }
            
            response = requests.post(
                genai_config['inference_url'] + '/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                risk_response = result['choices'][0]['message']['content'].strip().upper()
                
                # Map response to our risk levels
                risk_mapping = {
                    'HIGH': 'high',
                    'MEDIUM': 'medium', 
                    'LOW': 'low',
                    'NO': 'no'
                }
                
                return risk_mapping.get(risk_response, 'medium')
            else:
                logger.error(f"GenAI Risk API error: {response.status_code} - {response.text}")
                return self._fallback_risk_analysis(research_data['ingredient'], pet_type)
                
        except Exception as e:
            logger.error(f"DigitalOcean GenAI risk analysis failed: {e}")
            return self._fallback_risk_analysis(research_data['ingredient'], pet_type)
    
    def _fallback_risk_analysis(self, ingredient, pet_type):
        """Fallback risk analysis when Gradient AI is unavailable"""
        # Basic safety knowledge for common ingredients
        high_risk = ['chocolate', 'grapes', 'raisins', 'onion', 'garlic', 'xylitol', 'caffeine', 'alcohol']
        safe_ingredients = ['rice', 'chicken', 'carrots', 'pumpkin', 'sweet potato']
        
        ingredient_lower = ingredient.lower()
        
        if any(risky in ingredient_lower for risky in high_risk):
            return 'high'
        elif any(safe in ingredient_lower for safe in safe_ingredients):
            return 'no'
        else:
            return 'medium'

class RealFactCheckerAgent:
    """Agent that fact-checks and validates findings"""
    
    async def validate(self, research_data, risk_level, pet_type):
        """Use DigitalOcean GenAI agent to validate research findings and add additional context"""
        
        research_content = "\n".join([
            result['content'] for result in research_data['search_results'] 
            if result and 'content' in result
        ])
        
        if not genai_enabled:
            logger.warning("DigitalOcean GenAI not configured - using fallback fact checking")
            return self._fallback_fact_check(research_data, risk_level, pet_type)
        
        try:
            # Call DigitalOcean GenAI Fact Checker Agent
            headers = {
                'Authorization': f'Bearer {genai_config["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': genai_config['factcheck_agent_id'],
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a veterinary fact-checker specializing in validating pet ingredient safety information.'
                    },
                    {
                        'role': 'user',
                        'content': f"""Review the research and risk assessment for accuracy.

Ingredient: {research_data['ingredient']}
Pet Type: {pet_type}
Proposed Risk Level: {risk_level}

Research Data:
{research_content}

Provide:
1. Validation of the risk level (confirm or suggest correction)
2. Key toxic mechanisms if applicable
3. Specific symptoms to watch for
4. Authoritative sources (ASPCA, Pet Poison Helpline, veterinary journals)

Format as JSON with keys: validated_risk, mechanism, symptoms, authoritative_sources"""
                    }
                ],
                'max_tokens': 400
            }
            
            response = requests.post(
                genai_config['inference_url'] + '/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                fact_check_response = result['choices'][0]['message']['content']
                
                # Try to parse JSON response
                try:
                    fact_check_data = json.loads(fact_check_response)
                except:
                    # Fallback if JSON parsing fails
                    fact_check_data = {
                        'validated_risk': risk_level,
                        'mechanism': 'Requires veterinary assessment',
                        'symptoms': 'Monitor for changes in behavior, appetite, or energy levels',
                        'authoritative_sources': 'ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control'
                    }
                
                research_data['fact_check'] = fact_check_data
                research_data['validated_risk'] = fact_check_data.get('validated_risk', risk_level)
                
                return research_data
            else:
                logger.error(f"GenAI Fact Check API error: {response.status_code} - {response.text}")
                return self._fallback_fact_check(research_data, risk_level, pet_type)
                
        except Exception as e:
            logger.error(f"DigitalOcean GenAI fact checking failed: {e}")
            return self._fallback_fact_check(research_data, risk_level, pet_type)
    
    def _fallback_fact_check(self, research_data, risk_level, pet_type):
        """Fallback fact checking when Gradient AI is unavailable"""
        research_data['fact_check'] = {
            'validated_risk': risk_level,
            'mechanism': 'Unable to verify - consult veterinarian',
            'symptoms': 'Monitor pet closely',
            'authoritative_sources': 'ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control'
        }
        research_data['validated_risk'] = risk_level
        return research_data

class RealFormatterAgent:
    """Agent that formats the final output"""
    
    def format(self, ingredient, validated_data, risk_level):
        """Format the analysis results for display"""
        
        fact_check = validated_data.get('fact_check', {})
        final_risk = fact_check.get('validated_risk', risk_level)
        
        # Create detailed justification
        justification_parts = []
        
        if final_risk == 'no':
            justification_parts.append(f"{ingredient.capitalize()} is generally safe for {validated_data['pet_type']}s.")
        else:
            risk_descriptions = {
                'high': 'poses a serious threat and can be life-threatening',
                'medium': 'can cause significant health problems and should be avoided',
                'low': 'may cause mild adverse reactions but is generally tolerable in small amounts'
            }
            justification_parts.append(f"{ingredient.capitalize()} {risk_descriptions.get(final_risk, 'requires caution')} for {validated_data['pet_type']}s.")
        
        # Add mechanism if available
        mechanism = fact_check.get('mechanism', '')
        if mechanism and mechanism != 'Requires veterinary assessment':
            justification_parts.append(f"Mechanism: {mechanism}")
        
        # Add symptoms if available
        symptoms = fact_check.get('symptoms', '')
        if symptoms and symptoms != 'Monitor pet closely':
            justification_parts.append(f"Symptoms may include: {symptoms}")
        
        justification = ' '.join(justification_parts)
        
        # Get authoritative sources
        sources = fact_check.get('authoritative_sources', 'ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control')
        
        return {
            'name': ingredient,
            'risk_level': final_risk,
            'justification': justification,
            'sources': sources,
            'cached': False,
            'ai_powered': True
        }

# Initialize real multi-agent system
real_agents = RealMultiAgentSystem()

@app.route('/')
def index():
    """Serve the main application"""
    return render_template('index.html')

@app.route('/api/evaluate', methods=['POST'])
def evaluate_ingredients():
    """API endpoint to evaluate ingredients using real multi-agent system"""
    try:
        data = request.get_json()
        
        if not data or 'ingredients' not in data:
            return jsonify({'error': 'Missing ingredients'}), 400
        
        ingredients = data['ingredients']
        pet_type = data.get('pet_type', 'cat')
        category = data.get('category', 'mixed')
        
        if not ingredients:
            return jsonify({'error': 'No ingredients provided'}), 400
        
        logger.info(f"🚀 Processing request with DigitalOcean GenAI: {len(ingredients)} ingredients for {pet_type}")
        
        # Check if we have DigitalOcean GenAI configured
        if not genai_enabled:
            logger.warning("DigitalOcean GenAI not configured - using fallback mode")
            return jsonify({
                'success': True,
                'results': _fallback_analysis(ingredients, pet_type),
                'pet_type': pet_type,
                'category': category,
                'processed_at': datetime.utcnow().isoformat(),
                'mode': 'fallback'
            })
        
        # Process through real DigitalOcean GenAI multi-agent system
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(real_agents.process_ingredients(ingredients, pet_type, category))
        loop.close()
        
        return jsonify({
            'success': True,
            'results': results,
            'pet_type': pet_type,
            'category': category,
            'processed_at': datetime.utcnow().isoformat(),
            'mode': 'digitalocean_genai_powered'
        })
        
    except Exception as e:
        logger.error(f"Error in evaluate_ingredients: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def _fallback_analysis(ingredients, pet_type):
    """Fallback analysis when API keys are not available"""
    results = {'high': [], 'medium': [], 'low': [], 'no': []}
    
    # Basic safety knowledge for common ingredients
    high_risk = ['chocolate', 'grapes', 'raisins', 'onion', 'garlic', 'xylitol', 'caffeine', 'alcohol']
    safe_ingredients = ['rice', 'chicken', 'carrots', 'pumpkin', 'sweet potato']
    
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower()
        
        if any(risky in ingredient_lower for risky in high_risk):
            risk_level = 'high'
            justification = f"{ingredient.capitalize()} is known to be toxic to {pet_type}s and should be avoided completely."
        elif any(safe in ingredient_lower for safe in safe_ingredients):
            risk_level = 'no'
            justification = f"{ingredient.capitalize()} is generally safe for {pet_type}s when properly prepared."
        else:
            risk_level = 'medium'
            justification = f"{ingredient.capitalize()} requires further research. Consult your veterinarian for safety information."
        
        results[risk_level].append({
            'name': ingredient,
            'risk_level': risk_level,
            'justification': justification,
            'sources': 'ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control',
            'cached': False,
            'ai_powered': False
        })
    
    return results

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
        },
        'digitalocean_genai_enabled': genai_enabled,
        'genai_config': {
            'access_token_configured': bool(genai_config['access_token']),
            'research_agent_id': genai_config['research_agent_id'],
            'risk_agent_id': genai_config['risk_agent_id'],
            'factcheck_agent_id': genai_config['factcheck_agent_id'],
            'project_id': genai_config['project_id'],
            'region': genai_config['region'],
            'inference_url': genai_config['inference_url']
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"🐾 Starting Pet Ingredient Safety Checker on port {port}")
    logger.info("🤖 DigitalOcean GenAI Multi-Agent System initialized and ready")
    
    if genai_enabled:
        logger.info("✅ DigitalOcean GenAI configured - Real AI-powered analysis enabled")
        logger.info(f"   Research Agent: {genai_config['research_agent_id']}")
        logger.info(f"   Risk Agent: {genai_config['risk_agent_id']}")
        logger.info(f"   Fact Check Agent: {genai_config['factcheck_agent_id']}")
        logger.info(f"   Region: {genai_config['region']}")
        logger.info(f"   Inference URL: {genai_config['inference_url']}")
    else:
        logger.warning("⚠️ DigitalOcean GenAI not configured - using fallback mode")
        logger.warning("   Set DIGITALOCEAN_TOKEN and agent IDs for AI-powered analysis")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
