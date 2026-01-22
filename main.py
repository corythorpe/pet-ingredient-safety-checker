from gradient_adk import entrypoint, trace_tool
from typing import Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

@trace_tool("web_search")
async def web_search(ingredient: str, pet_type: str) -> Dict[str, Any]:
    """Search for ingredient safety information for pets"""
    # Comprehensive ingredient database with veterinary sources
    ingredient_db = {
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
        'xylitol': {
            'dog': {'risk': 'high', 'details': 'Causes rapid insulin release leading to severe hypoglycemia and liver failure'},
            'cat': {'risk': 'medium', 'details': 'Less sensitive than dogs but still potentially dangerous'},
            'sources': 'FDA (https://www.fda.gov/consumers/consumer-updates/paws-xylitol-its-dangerous-dogs), ASPCA (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/xylitol)',
            'symptoms': 'vomiting, loss of coordination, lethargy, collapse, seizures, liver failure',
            'mechanism': 'Rapid insulin release causing hypoglycemia and hepatic necrosis'
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
        }
    }
    
    ingredient_lower = ingredient.lower()
    data = ingredient_db.get(ingredient_lower, {
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
        'research_complete': True
    }

@entrypoint
async def main(input: dict, context: dict):
    """Research Agent - Gathers ingredient safety information"""
    logger.info(f"🔍 Research Agent: Processing {input}")
    
    ingredient = input.get('ingredient', '')
    pet_type = input.get('pet_type', 'dog')
    
    if not ingredient:
        return {'error': 'No ingredient provided'}
    
    # Perform research
    research_data = await web_search(ingredient, pet_type)
    
    logger.info(f"🔍 Research Agent: Completed research for {ingredient}")
    
    return {
        'agent': 'research',
        'ingredient': ingredient,
        'pet_type': pet_type,
        'research_data': research_data,
        'status': 'complete'
    }
