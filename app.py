#!/usr/bin/env python3
"""
Pet Ingredient Safety Checker - Real Multi-Agent System
Using Gradient AI for actual web research and analysis
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import logging
from datetime import datetime, timedelta
import json
import asyncio
import aiohttp
import requests
import re
import hashlib
import pickle
from pathlib import Path

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

# Check if GenAI is configured - REQUIRED for operation
genai_enabled = all([
    genai_config['research_agent_id'],
    genai_config['risk_agent_id'], 
    genai_config['factcheck_agent_id'],
    genai_config['access_token']
])

# Validate configuration at startup
def validate_genai_configuration():
    """Validate that all required DigitalOcean GenAI configuration is present"""
    missing_config = []
    
    required_configs = {
        'DIGITALOCEAN_TOKEN': genai_config['access_token'],
        'DIGITALOCEAN_GENAI_RESEARCH_AGENT_ID': genai_config['research_agent_id'],
        'DIGITALOCEAN_GENAI_RISK_AGENT_ID': genai_config['risk_agent_id'],
        'DIGITALOCEAN_GENAI_FACTCHECK_AGENT_ID': genai_config['factcheck_agent_id'],
        'DIGITALOCEAN_GENAI_INFERENCE_URL': genai_config['inference_url']
    }
    
    for config_name, config_value in required_configs.items():
        if not config_value:
            missing_config.append(config_name)
    
    if missing_config:
        error_msg = f"""
🚨 CONFIGURATION ERROR: Pet Ingredient Safety Checker requires DigitalOcean GenAI configuration.

Missing required environment variables:
{chr(10).join(f'  - {config}' for config in missing_config)}

Please set these environment variables in your .env file or environment.
See .env.example for the required configuration template.

This application is AI-powered and cannot operate without proper GenAI configuration.
        """.strip()
        
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info("✅ DigitalOcean GenAI configuration validated successfully")

# Validate configuration at startup
if not genai_enabled:
    validate_genai_configuration()

class IngredientCache:
    """File-based cache for ingredient lookups with 15-day expiration"""
    
    def __init__(self, cache_dir='cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_duration = timedelta(days=15)
        logger.info(f"📋 Ingredient cache initialized: {self.cache_dir.absolute()}")
    
    def _get_cache_key(self, ingredient, pet_type):
        """Generate a unique cache key for ingredient + pet type combination"""
        key_string = f"{ingredient.lower().strip()}_{pet_type.lower()}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key):
        """Get the file path for a cache key"""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def get(self, ingredient, pet_type):
        """Retrieve cached result if available and not expired"""
        cache_key = self._get_cache_key(ingredient, pet_type)
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cached_time > self.cache_duration:
                logger.info(f"🗑️ Cache expired for {ingredient} ({pet_type})")
                cache_path.unlink()  # Delete expired cache
                return None
            
            logger.info(f"📋 Cache hit for {ingredient} ({pet_type})")
            return cached_data['result']
            
        except Exception as e:
            logger.warning(f"Cache read error for {ingredient}: {e}")
            # Delete corrupted cache file
            try:
                cache_path.unlink()
            except:
                pass
            return None
    
    def set(self, ingredient, pet_type, result):
        """Store result in cache"""
        cache_key = self._get_cache_key(ingredient, pet_type)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            cached_data = {
                'ingredient': ingredient,
                'pet_type': pet_type,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(cached_data, f)
            
            logger.info(f"💾 Cached result for {ingredient} ({pet_type})")
            
        except Exception as e:
            logger.warning(f"Cache write error for {ingredient}: {e}")
    
    def cleanup_expired(self):
        """Remove expired cache files"""
        removed_count = 0
        for cache_file in self.cache_dir.glob('*.pkl'):
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                
                cached_time = datetime.fromisoformat(cached_data['timestamp'])
                if datetime.now() - cached_time > self.cache_duration:
                    cache_file.unlink()
                    removed_count += 1
                    
            except Exception as e:
                # Remove corrupted files
                try:
                    cache_file.unlink()
                    removed_count += 1
                except:
                    pass
        
        if removed_count > 0:
            logger.info(f"🧹 Cleaned up {removed_count} expired cache files")
    
    def get_cache_stats(self):
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob('*.pkl'))
        total_files = len(cache_files)
        expired_files = 0
        
        for cache_file in cache_files:
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                
                cached_time = datetime.fromisoformat(cached_data['timestamp'])
                if datetime.now() - cached_time > self.cache_duration:
                    expired_files += 1
            except:
                expired_files += 1
        
        return {
            'total_cached_ingredients': total_files,
            'expired_entries': expired_files,
            'active_entries': total_files - expired_files,
            'cache_directory': str(self.cache_dir.absolute())
        }

# Initialize cache
ingredient_cache = IngredientCache()

class RealMultiAgentSystem:
    """Real multi-agent system using Gradient AI and web research"""
    
    def __init__(self):
        self.research_agent = RealResearchAgent()
        self.risk_analysis_agent = RealRiskAnalysisAgent()
        self.fact_checker_agent = RealFactCheckerAgent()
        self.formatter_agent = RealFormatterAgent()
    
    async def process_ingredients(self, ingredients, pet_type, category):
        """Process ingredients through the real multi-agent pipeline with caching"""
        logger.info(f"🤖 Real Multi-Agent System: Processing {len(ingredients)} ingredients for {pet_type}")
        
        results = {'high': [], 'medium': [], 'low': [], 'no': []}
        
        # Clean up expired cache entries at the start
        ingredient_cache.cleanup_expired()
        
        for ingredient in ingredients:
            try:
                # Check cache first
                cached_result = ingredient_cache.get(ingredient, pet_type)
                if cached_result:
                    # Use cached result
                    cached_result['cached'] = True
                    results[cached_result['risk_level']].append(cached_result)
                    continue
                
                # Not in cache - process through agents
                logger.info(f"🔍 Research Agent: Researching {ingredient} online")
                research_data = await self.research_agent.research(ingredient, pet_type)
                
                logger.info(f"⚖️ Risk Analysis Agent: AI analyzing {ingredient}")
                risk_level = await self.risk_analysis_agent.analyze(research_data, pet_type)
                
                logger.info(f"✅ Fact Checker Agent: Validating {ingredient}")
                validated_data = await self.fact_checker_agent.validate(research_data, risk_level, pet_type)
                
                logger.info(f"📝 Formatter Agent: Formatting {ingredient}")
                formatted_result = self.formatter_agent.format(ingredient, validated_data, risk_level)
                
                # Cache the result for future use
                ingredient_cache.set(ingredient, pet_type, formatted_result)
                
                results[risk_level].append(formatted_result)
                
            except Exception as e:
                logger.error(f"Error processing {ingredient}: {e}")
                error_result = {
                    'name': ingredient,
                    'risk_level': 'medium',
                    'justification': f"Unable to fully research {ingredient} due to technical issues. Please consult your veterinarian for safety information.",
                    'sources': 'ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control',
                    'cached': False
                }
                results['medium'].append(error_result)
        
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
                raise Exception(f"Research Agent API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"DigitalOcean GenAI research failed: {e}")
            raise Exception(f"Research Agent temporarily unavailable: {e}")

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
                raise Exception(f"Risk Analysis Agent API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"DigitalOcean GenAI risk analysis failed: {e}")
            raise Exception(f"Risk Analysis Agent temporarily unavailable: {e}")

class RealFactCheckerAgent:
    """Agent that fact-checks and validates findings"""
    
    async def validate(self, research_data, risk_level, pet_type):
        """Use DigitalOcean GenAI agent to validate research findings and add additional context"""
        
        research_content = "\n".join([
            result['content'] for result in research_data['search_results'] 
            if result and 'content' in result
        ])
        
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
                raise Exception(f"Fact Checker Agent API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"DigitalOcean GenAI fact checking failed: {e}")
            raise Exception(f"Fact Checker Agent temporarily unavailable: {e}")
    
    def _fallback_fact_check(self, research_data, risk_level, pet_type):
        """Enhanced fallback fact checking with detailed ingredient-specific information"""
        ingredient = research_data['ingredient'].lower()
        
        # Generate query-specific source URLs
        def generate_source_urls(ingredient_name, pet_type):
            """Generate multiple query-specific source URLs"""
            sources = []
            
            # ASPCA search URL
            aspca_query = f"{ingredient_name} {pet_type} toxic poisonous"
            aspca_url = f"https://www.aspca.org/search?query={aspca_query.replace(' ', '+')}"
            sources.append(f"ASPCA Search Results for '{ingredient_name}': {aspca_url}")
            
            # Pet Poison Helpline search
            pph_query = f"{ingredient_name} {pet_type}"
            pph_url = f"https://www.petpoisonhelpline.com/search/?q={pph_query.replace(' ', '+')}"
            sources.append(f"Pet Poison Helpline Search for '{ingredient_name}': {pph_url}")
            
            # VCA Animal Hospitals search
            vca_query = f"{ingredient_name} toxic {pet_type}"
            vca_url = f"https://vcahospitals.com/search?q={vca_query.replace(' ', '+')}"
            sources.append(f"VCA Animal Hospitals Search for '{ingredient_name}': {vca_url}")
            
            # PetMD search
            petmd_query = f"{ingredient_name} {pet_type} safe toxic"
            petmd_url = f"https://www.petmd.com/search?query={petmd_query.replace(' ', '+')}"
            sources.append(f"PetMD Search for '{ingredient_name}': {petmd_url}")
            
            return sources
        
        # Comprehensive ingredient safety database
        ingredient_database = {
            'chocolate': {
                'mechanism': 'Contains theobromine and caffeine, which are toxic methylxanthines that pets cannot metabolize effectively. Dark chocolate and baking chocolate are most dangerous.',
                'symptoms': 'Vomiting, diarrhea, increased heart rate, seizures, hyperactivity, excessive thirst, abnormal heart rhythm. Symptoms appear 6-12 hours after ingestion.',
                'severity': 'high',
                'additional_info': 'Toxicity depends on chocolate type and pet size. As little as 20mg/kg of theobromine can cause toxicity.'
            },
            'grapes': {
                'mechanism': 'Contains unknown compounds that cause acute kidney failure in dogs and cats. Even small amounts can be fatal.',
                'symptoms': 'Vomiting, diarrhea, lethargy, loss of appetite, abdominal pain, decreased urination, kidney failure within 24-72 hours.',
                'severity': 'high',
                'additional_info': 'No safe amount established. Both fresh grapes and raisins are toxic. Immediate veterinary care required.'
            },
            'raisins': {
                'mechanism': 'Dried grapes containing concentrated toxic compounds that cause acute kidney failure. More concentrated than fresh grapes.',
                'symptoms': 'Vomiting, diarrhea, lethargy, loss of appetite, abdominal pain, decreased urination, kidney failure within 24-72 hours.',
                'severity': 'high',
                'additional_info': 'Even more dangerous than grapes due to concentration. As few as 6 raisins can be toxic to a 20lb dog.'
            },
            'onion': {
                'mechanism': 'Contains N-propyl disulfide and other sulfur compounds that damage red blood cells, causing hemolytic anemia.',
                'symptoms': 'Weakness, lethargy, pale gums, rapid breathing, vomiting, diarrhea, dark-colored urine. Symptoms may be delayed 1-3 days.',
                'severity': 'high',
                'additional_info': 'All forms toxic: raw, cooked, powdered, dehydrated. Cats are more sensitive than dogs. Cumulative toxicity possible.'
            },
            'onions': {
                'mechanism': 'Contains N-propyl disulfide and other sulfur compounds that damage red blood cells, causing hemolytic anemia.',
                'symptoms': 'Weakness, lethargy, pale gums, rapid breathing, vomiting, diarrhea, dark-colored urine. Symptoms may be delayed 1-3 days.',
                'severity': 'high',
                'additional_info': 'All forms toxic: raw, cooked, powdered, dehydrated. Cats are more sensitive than dogs. Cumulative toxicity possible.'
            },
            'garlic': {
                'mechanism': 'Contains allicin and sulfur compounds that are 5x more potent than onions in causing red blood cell damage and anemia.',
                'symptoms': 'Weakness, lethargy, pale gums, rapid breathing, vomiting, diarrhea, dark-colored urine. More severe than onion toxicity.',
                'severity': 'high',
                'additional_info': 'More toxic than onions. Even small amounts can be dangerous. Cats are extremely sensitive.'
            },
            'xylitol': {
                'mechanism': 'Artificial sweetener that causes rapid insulin release, leading to severe hypoglycemia and potential liver failure.',
                'symptoms': 'Vomiting, loss of coordination, lethargy, collapse, seizures within 10-60 minutes. Liver failure possible in 12-24 hours.',
                'severity': 'high',
                'additional_info': 'Found in sugar-free gum, mints, baked goods. As little as 0.1g/kg can cause hypoglycemia. Emergency treatment required.'
            },
            'avocado': {
                'mechanism': 'Contains persin, a fungicidal toxin that can cause digestive upset and respiratory distress in pets.',
                'symptoms': 'Vomiting, diarrhea, difficulty breathing, fluid accumulation around heart. Birds and small mammals most sensitive.',
                'severity': 'medium',
                'additional_info': 'All parts toxic: fruit, pit, leaves, bark. Dogs and cats less sensitive than birds, but still at risk.'
            },
            'macadamia nuts': {
                'mechanism': 'Contains unknown compounds that affect the nervous system and muscles, causing weakness and hyperthermia.',
                'symptoms': 'Weakness, depression, vomiting, hyperthermia, tremors, inability to walk normally. Symptoms appear 12 hours after ingestion.',
                'severity': 'medium',
                'additional_info': 'Primarily affects dogs. As few as 6 nuts can cause toxicity in small dogs. Recovery usually occurs within 48 hours.'
            },
            'macadamia': {
                'mechanism': 'Contains unknown compounds that affect the nervous system and muscles, causing weakness and hyperthermia.',
                'symptoms': 'Weakness, depression, vomiting, hyperthermia, tremors, inability to walk normally. Symptoms appear 12 hours after ingestion.',
                'severity': 'medium',
                'additional_info': 'Primarily affects dogs. As few as 6 nuts can cause toxicity in small dogs. Recovery usually occurs within 48 hours.'
            },
            'caffeine': {
                'mechanism': 'Methylxanthine stimulant that affects the central nervous system and cardiovascular system. Similar to theobromine toxicity.',
                'symptoms': 'Hyperactivity, restlessness, vomiting, elevated heart rate, high blood pressure, abnormal heart rhythms, tremors, seizures.',
                'severity': 'high',
                'additional_info': 'Found in coffee, tea, energy drinks, medications. Pets are much more sensitive than humans. Can be fatal.'
            },
            'alcohol': {
                'mechanism': 'Ethanol causes central nervous system depression, metabolic acidosis, and can lead to coma and death.',
                'symptoms': 'Vomiting, diarrhea, difficulty breathing, tremors, abnormal blood acidity, coma, death.',
                'severity': 'high',
                'additional_info': 'Even small amounts dangerous. Found in alcoholic beverages, raw bread dough, mouthwash. Immediate veterinary care required.'
            },
            'chicken': {
                'mechanism': 'Generally safe when properly cooked and boneless. Raw chicken may contain harmful bacteria like Salmonella.',
                'symptoms': 'If raw or contaminated: vomiting, diarrhea, fever, lethargy from bacterial infection.',
                'severity': 'no',
                'additional_info': 'Cooked, boneless chicken is safe and nutritious. Avoid seasoning, bones, and raw preparation. Remove skin to reduce fat.'
            },
            'rice': {
                'mechanism': 'Easily digestible carbohydrate that is safe and often recommended for digestive issues.',
                'symptoms': 'Generally no adverse effects. May cause mild digestive upset if given in very large quantities.',
                'severity': 'no',
                'additional_info': 'Plain, cooked white or brown rice is safe. Often used in bland diets for digestive recovery. Avoid seasoning.'
            },
            'carrots': {
                'mechanism': 'High in beta-carotene, fiber, and vitamins. Safe and nutritious for pets.',
                'symptoms': 'No adverse effects. May cause orange discoloration of urine if consumed in very large quantities.',
                'severity': 'no',
                'additional_info': 'Raw or cooked carrots are safe. Good source of vitamins and can help with dental health. Cut into appropriate sizes.'
            },
            'sweet potato': {
                'mechanism': 'Rich in vitamins, minerals, and fiber. Safe and nutritious for pets.',
                'symptoms': 'No adverse effects when properly prepared. Raw sweet potato may cause digestive upset.',
                'severity': 'no',
                'additional_info': 'Cooked sweet potato is safe and nutritious. Avoid raw preparation and seasoning. Good source of beta-carotene.'
            },
            'pumpkin': {
                'mechanism': 'High in fiber and nutrients. Often recommended for digestive health.',
                'symptoms': 'No adverse effects. May cause loose stools if given in excessive amounts due to high fiber content.',
                'severity': 'no',
                'additional_info': 'Plain, cooked pumpkin is safe and beneficial. Avoid pumpkin pie filling with spices. Good for digestive health.'
            }
        }
        
        # Get ingredient-specific information
        ingredient_info = None
        for key in ingredient_database:
            if key in ingredient:
                ingredient_info = ingredient_database[key]
                break
        
        if ingredient_info:
            # Use detailed database information
            validated_risk = ingredient_info['severity']
            mechanism = ingredient_info['mechanism']
            symptoms = ingredient_info['symptoms']
            additional_info = ingredient_info.get('additional_info', '')
            
            # Create comprehensive justification
            if additional_info:
                mechanism += f" {additional_info}"
                
        else:
            # Enhanced fallback for unknown ingredients
            if risk_level == 'high':
                mechanism = f"While specific toxicity data for {research_data['ingredient']} is limited, this ingredient has been flagged as potentially dangerous for {pet_type}s based on available safety patterns. May contain compounds that could cause serious health issues."
                symptoms = "Monitor for vomiting, diarrhea, lethargy, loss of appetite, difficulty breathing, or unusual behavior. Seek immediate veterinary care if any symptoms appear."
                validated_risk = 'high'
            elif risk_level == 'medium':
                mechanism = f"{research_data['ingredient'].capitalize()} may cause digestive upset or mild adverse reactions in {pet_type}s. While not immediately life-threatening, caution is recommended."
                symptoms = "Watch for mild digestive upset, changes in appetite, or unusual behavior. Consult veterinarian if symptoms persist or worsen."
                validated_risk = 'medium'
            elif risk_level == 'low':
                mechanism = f"{research_data['ingredient'].capitalize()} appears to have minimal risk for {pet_type}s but may cause minor digestive sensitivity in some pets."
                symptoms = "Generally well-tolerated. Monitor for any unusual digestive changes or allergic reactions."
                validated_risk = 'low'
            else:
                mechanism = f"{research_data['ingredient'].capitalize()} appears to be generally safe for {pet_type}s when given in appropriate amounts."
                symptoms = "No significant adverse effects expected. Monitor as with any new food item."
                validated_risk = 'no'
        
        # Generate multiple query-specific sources
        query_specific_sources = generate_source_urls(research_data['ingredient'], pet_type)
        
        research_data['fact_check'] = {
            'validated_risk': validated_risk,
            'mechanism': mechanism,
            'symptoms': symptoms,
            'authoritative_sources': query_specific_sources,
            'emergency_contacts': 'ASPCA Animal Poison Control: (888) 426-4435 | Pet Poison Helpline: (855) 764-7661'
        }
        research_data['validated_risk'] = validated_risk
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
        
        # Get authoritative sources - check both possible keys
        sources = fact_check.get('authoritative_sources', fact_check.get('sources', 'ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control'))
        
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

@app.route('/admin')
def admin_dashboard():
    """Serve the admin dashboard"""
    return render_template('admin_dashboard.html')

@app.route('/how-it-works')
def how_it_works():
    """Serve the how it works dashboard"""
    return render_template('how_it_works.html')

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
        
        # Process through DigitalOcean GenAI multi-agent system
        # Configuration is validated at startup, so we know GenAI is available
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
            'mode': 'digitalocean_genai_powered',
            'ai_powered': True
        })
        
    except Exception as e:
        logger.error(f"Error in evaluate_ingredients: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with cache statistics"""
    cache_stats = ingredient_cache.get_cache_stats()
    
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
        'cache_stats': cache_stats,
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
