// Pet Ingredient Safety Checker - Frontend JavaScript

class PetIngredientChecker {
    constructor() {
        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        this.evaluateBtn = document.getElementById('evaluateBtn');
        this.newSearchBtn = document.getElementById('newSearchBtn');
        this.ingredientsTextarea = document.getElementById('ingredients');
        this.petTypeSelect = document.getElementById('petType');
        this.categorySelect = document.getElementById('ingredientCategory');
        this.resultsSection = document.getElementById('results');
        this.resultsContent = document.getElementById('resultsContent');
        this.inputSection = document.querySelector('.input-section');
        this.btnText = this.evaluateBtn.querySelector('.btn-text');
        this.loadingSpinner = this.evaluateBtn.querySelector('.loading-spinner');
    }

    bindEvents() {
        this.evaluateBtn.addEventListener('click', () => this.handleEvaluate());
        this.newSearchBtn.addEventListener('click', () => this.handleNewSearch());
        
        // Enable evaluate button only when ingredients are entered
        this.ingredientsTextarea.addEventListener('input', () => {
            const hasIngredients = this.ingredientsTextarea.value.trim().length > 0;
            this.evaluateBtn.disabled = !hasIngredients;
        });
    }

    async handleEvaluate() {
        const ingredients = this.parseIngredients(this.ingredientsTextarea.value);
        const petType = this.petTypeSelect.value;
        const category = this.categorySelect.value;

        if (ingredients.length === 0) {
            alert('Please enter at least one ingredient.');
            return;
        }

        this.showLoading(true);

        try {
            // Call backend API with real multi-agent system
            const response = await fetch('/api/evaluate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ingredients: ingredients,
                    pet_type: petType,
                    category: category
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displayResults(data.results, petType, category);
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Error processing ingredients:', error);
            alert('An error occurred while processing ingredients. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }

    parseIngredients(text) {
        return text
            .split(/[,\n]/)
            .map(ingredient => ingredient.trim())
            .filter(ingredient => ingredient.length > 0)
            .map(ingredient => ingredient.toLowerCase());
    }

    showLoading(isLoading) {
        this.evaluateBtn.disabled = isLoading;
        if (isLoading) {
            this.btnText.style.display = 'none';
            this.loadingSpinner.style.display = 'inline';
        } else {
            this.btnText.style.display = 'inline';
            this.loadingSpinner.style.display = 'none';
        }
    }

    displayResults(results, petType, category) {
        this.inputSection.style.display = 'none';
        this.resultsSection.style.display = 'block';

        const petEmoji = petType === 'cat' ? '🐱' : '🐕';
        const categoryEmoji = category === 'food' ? '🍖' : category === 'medication' ? '💊' : '🔍';
        const categoryText = category === 'food' ? 'Food' : category === 'medication' ? 'Medication' : 'Food & Medication';
        
        const resultsHeader = this.resultsSection.querySelector('h2');
        resultsHeader.textContent = `${petEmoji} ${categoryEmoji} ${categoryText} Safety Assessment for ${petType.charAt(0).toUpperCase() + petType.slice(1)}s`;

        this.resultsContent.innerHTML = this.generateResultsHTML(results);
    }

    generateResultsHTML(results) {
        const categories = [
            { key: 'high', label: 'High Risk', icon: '⚠️', description: 'Potentially life-threatening - avoid completely' },
            { key: 'medium', label: 'Medium Risk', icon: '⚡', description: 'May cause serious health issues - use caution' },
            { key: 'low', label: 'Low Risk', icon: '⚪', description: 'May cause mild reactions - monitor closely' },
            { key: 'no', label: 'No Risk', icon: '✅', description: 'Generally safe for consumption' }
        ];

        return categories.map(category => {
            const ingredients = results[category.key] || [];
            const hasIngredients = ingredients.length > 0;

            return `
                <div class="risk-category">
                    <div class="risk-header ${category.key}-risk">
                        <span>${category.icon}</span>
                        <span>${category.label}</span>
                        <span>(${ingredients.length} ingredient${ingredients.length !== 1 ? 's' : ''})</span>
                    </div>
                    ${hasIngredients ? 
                        ingredients.map(ingredient => `
                            <div class="ingredient-item">
                                <div class="ingredient-name">${this.capitalizeFirst(ingredient.name)}</div>
                                <div class="ingredient-justification">${ingredient.justification}</div>
                                <div class="ingredient-sources">
                                    <strong>Sources:</strong> ${ingredient.sources}
                                </div>
                            </div>
                        `).join('') :
                        `<div class="empty-category">No ingredients found in this category</div>`
                    }
                </div>
            `;
        }).join('');
    }

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    handleNewSearch() {
        this.inputSection.style.display = 'block';
        this.resultsSection.style.display = 'none';
        this.ingredientsTextarea.value = '';
        this.evaluateBtn.disabled = true;
    }
}

// Multi-Agent System Simulation
class MultiAgentSystem {
    constructor() {
        this.researchAgent = new ResearchAgent();
        this.riskAnalysisAgent = new RiskAnalysisAgent();
        this.factCheckerAgent = new FactCheckerAgent();
        this.formatterAgent = new FormatterAgent();
    }

    async processIngredients(ingredients, petType, category) {
        console.log(`Processing ${ingredients.length} ingredients for ${petType} (${category} category)...`);
        
        // Simulate processing delay
        await this.delay(2000);

        const results = { high: [], medium: [], low: [], no: [] };

        for (const ingredient of ingredients) {
            // Research Agent: Gather information
            const researchData = await this.researchAgent.research(ingredient, petType, category);
            
            // Risk Analysis Agent: Categorize risk
            const riskLevel = await this.riskAnalysisAgent.analyze(researchData, petType);
            
            // Fact Checker Agent: Validate findings
            const validatedData = await this.factCheckerAgent.validate(researchData, riskLevel);
            
            // Formatter Agent: Structure output
            const formattedResult = await this.formatterAgent.format(ingredient, validatedData, riskLevel);
            
            results[riskLevel].push(formattedResult);
        }

        return results;
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Research Agent - Simulates web research for ingredient safety
class ResearchAgent {
    constructor() {
        this.knowledgeBase = this.initializeKnowledgeBase();
    }

    async research(ingredient, petType, category) {
        console.log(`Research Agent: Researching ${ingredient} for ${petType}s (${category} category)...`);
        await this.delay(300);

        const data = this.knowledgeBase[ingredient] || this.knowledgeBase['unknown'];
        return {
            ingredient,
            petType,
            category,
            toxicityData: data[petType] || data.general,
            sources: data.sources,
            symptoms: data.symptoms,
            mechanism: data.mechanism,
            ingredientType: data.type || 'unknown'
        };
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    initializeKnowledgeBase() {
        return {
            'chocolate': {
                dog: {
                    toxic: true,
                    severity: 'high',
                    details: 'Contains theobromine and caffeine, which dogs cannot metabolize effectively'
                },
                cat: {
                    toxic: true,
                    severity: 'high',
                    details: 'Contains theobromine and caffeine, highly toxic to cats'
                },
                sources: 'ASPCA Animal Poison Control Center (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/chocolate), Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/chocolate/)',
                symptoms: 'vomiting, diarrhea, seizures, cardiac arrhythmias, death',
                mechanism: 'Theobromine toxicity affecting cardiovascular and nervous systems',
                type: 'food'
            },
            'onion': {
                dog: {
                    toxic: true,
                    severity: 'high',
                    details: 'Contains N-propyl disulfide causing oxidative damage to red blood cells'
                },
                cat: {
                    toxic: true,
                    severity: 'high',
                    details: 'Extremely toxic - causes severe hemolytic anemia'
                },
                sources: 'ASPCA (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/onion), VCA Animal Hospitals (https://vcahospitals.com/know-your-pet/onion-garlic-chive-and-leek-toxicity-in-dogs)',
                symptoms: 'anemia, weakness, pale gums, difficulty breathing',
                mechanism: 'Oxidative damage to red blood cells leading to hemolytic anemia',
                type: 'food'
            },
            'garlic': {
                dog: {
                    toxic: true,
                    severity: 'high',
                    details: 'More potent than onions - causes severe oxidative damage'
                },
                cat: {
                    toxic: true,
                    severity: 'high',
                    details: 'Highly toxic - more dangerous than onions for cats'
                },
                sources: 'ASPCA (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/garlic), Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/garlic/)',
                symptoms: 'anemia, weakness, collapse, organ damage',
                mechanism: 'Allicin and other sulfur compounds cause oxidative red blood cell damage',
                type: 'food'
            },
            'grapes': {
                dog: {
                    toxic: true,
                    severity: 'high',
                    details: 'Unknown toxic compound causes acute kidney failure'
                },
                cat: {
                    toxic: true,
                    severity: 'medium',
                    details: 'Less documented in cats but potentially nephrotoxic'
                },
                sources: 'ASPCA (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/grape), FDA (https://www.fda.gov/animal-veterinary/animal-health-literacy/dangers-grapes-and-raisins-dogs)',
                symptoms: 'vomiting, kidney failure, death',
                mechanism: 'Unknown nephrotoxic compound causing acute renal failure',
                type: 'food'
            },
            'raisins': {
                dog: {
                    toxic: true,
                    severity: 'high',
                    details: 'Concentrated grape toxicity - even small amounts dangerous'
                },
                cat: {
                    toxic: true,
                    severity: 'medium',
                    details: 'Potentially nephrotoxic like grapes'
                },
                sources: 'Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/raisin/), ASPCA (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/grape)',
                symptoms: 'kidney failure, vomiting, lethargy',
                mechanism: 'Concentrated nephrotoxic compounds from grapes',
                type: 'food'
            },
            'chicken': {
                dog: {
                    toxic: false,
                    severity: 'no',
                    details: 'Safe protein source when properly cooked'
                },
                cat: {
                    toxic: false,
                    severity: 'no',
                    details: 'Excellent protein source for cats'
                },
                sources: 'AVMA (https://www.avma.org/resources-tools/pet-owners/petcare/selecting-nutritious-pet-food), AAFCO (https://www.aafco.org/consumers/understanding-pet-food)',
                symptoms: 'none when properly prepared',
                mechanism: 'High-quality protein with essential amino acids',
                type: 'food'
            },
            'rice': {
                dog: {
                    toxic: false,
                    severity: 'no',
                    details: 'Easily digestible carbohydrate source'
                },
                cat: {
                    toxic: false,
                    severity: 'no',
                    details: 'Safe carbohydrate, though cats have limited carbohydrate needs'
                },
                sources: 'AAFCO (https://www.aafco.org/consumers/understanding-pet-food), VCA Animal Hospitals (https://vcahospitals.com/know-your-pet/dog-feeding-guide)',
                symptoms: 'none',
                mechanism: 'Provides digestible carbohydrates and energy',
                type: 'food'
            },
            'avocado': {
                dog: {
                    toxic: true,
                    severity: 'medium',
                    details: 'Contains persin, which can cause digestive upset'
                },
                cat: {
                    toxic: true,
                    severity: 'medium',
                    details: 'Persin toxicity can cause digestive and cardiac issues'
                },
                sources: 'ASPCA (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/avocado), Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/avocado/)',
                symptoms: 'vomiting, diarrhea, difficulty breathing',
                mechanism: 'Persin compound causes gastrointestinal and cardiac effects',
                type: 'food'
            },
            // MEDICATION INGREDIENTS
            'ibuprofen': {
                dog: {
                    toxic: true,
                    severity: 'high',
                    details: 'NSAIDs are extremely dangerous - can cause kidney failure, liver damage, and death'
                },
                cat: {
                    toxic: true,
                    severity: 'high',
                    details: 'Highly toxic - cats cannot metabolize NSAIDs, leading to severe organ damage'
                },
                sources: 'ASPCA (https://www.aspca.org/pet-care/animal-poison-control/people-foods-avoid-feeding-your-pets), Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/ibuprofen/), VCA Animal Hospitals (https://vcahospitals.com/know-your-pet/ibuprofen-toxicity-in-dogs-and-cats)',
                symptoms: 'vomiting, diarrhea, loss of appetite, kidney failure, liver damage, seizures, coma, death',
                mechanism: 'Inhibits cyclooxygenase enzymes causing gastrointestinal ulceration and renal toxicity',
                type: 'medication'
            },
            'acetaminophen': {
                dog: {
                    toxic: true,
                    severity: 'high',
                    details: 'Causes liver damage and methemoglobinemia - potentially fatal'
                },
                cat: {
                    toxic: true,
                    severity: 'high',
                    details: 'Extremely toxic - cats lack glucuronidation enzymes, making acetaminophen lethal'
                },
                sources: 'ASPCA (https://www.aspca.org/pet-care/animal-poison-control/people-foods-avoid-feeding-your-pets), Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/acetaminophen/), VCA Animal Hospitals (https://vcahospitals.com/know-your-pet/acetaminophen-toxicity-in-cats)',
                symptoms: 'difficulty breathing, brown gums, liver failure, swelling of face and paws, death',
                mechanism: 'Depletes glutathione causing hepatotoxicity and methemoglobinemia',
                type: 'medication'
            },
            'aspirin': {
                dog: {
                    toxic: true,
                    severity: 'medium',
                    details: 'Can cause gastrointestinal bleeding and kidney problems - sometimes used under veterinary supervision'
                },
                cat: {
                    toxic: true,
                    severity: 'high',
                    details: 'Highly toxic - cats metabolize salicylates very slowly, leading to accumulation'
                },
                sources: 'Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/aspirin/), VCA Animal Hospitals (https://vcahospitals.com/know-your-pet/aspirin-poisoning-in-cats), AVMA (https://www.avma.org/resources-tools/pet-owners/petcare/aspirin-and-other-nsaids)',
                symptoms: 'vomiting, diarrhea, loss of appetite, breathing difficulties, seizures',
                mechanism: 'Salicylate toxicity affecting multiple organ systems',
                type: 'medication'
            },
            'xylitol': {
                dog: {
                    toxic: true,
                    severity: 'high',
                    details: 'Causes rapid insulin release leading to severe hypoglycemia and liver failure'
                },
                cat: {
                    toxic: true,
                    severity: 'medium',
                    details: 'Less sensitive than dogs but still potentially dangerous'
                },
                sources: 'FDA (https://www.fda.gov/consumers/consumer-updates/paws-xylitol-its-dangerous-dogs), ASPCA (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/xylitol), Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/xylitol/)',
                symptoms: 'vomiting, loss of coordination, lethargy, collapse, seizures, liver failure',
                mechanism: 'Rapid insulin release causing hypoglycemia and hepatic necrosis',
                type: 'medication'
            },
            'caffeine': {
                dog: {
                    toxic: true,
                    severity: 'high',
                    details: 'Methylxanthine toxicity similar to chocolate but more concentrated'
                },
                cat: {
                    toxic: true,
                    severity: 'high',
                    details: 'Highly toxic - cats are very sensitive to methylxanthines'
                },
                sources: 'ASPCA (https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/coffee), Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/caffeine/), VCA Animal Hospitals (https://vcahospitals.com/know-your-pet/caffeine-toxicity-in-pets)',
                symptoms: 'restlessness, rapid breathing, heart palpitations, muscle tremors, seizures',
                mechanism: 'Methylxanthine toxicity affecting cardiovascular and nervous systems',
                type: 'medication'
            },
            'diphenhydramine': {
                dog: {
                    toxic: true,
                    severity: 'medium',
                    details: 'Antihistamine that can cause sedation and anticholinergic effects - sometimes used under veterinary guidance'
                },
                cat: {
                    toxic: true,
                    severity: 'medium',
                    details: 'Can cause sedation and anticholinergic toxicity in cats'
                },
                sources: 'Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/diphenhydramine/), VCA Animal Hospitals (https://vcahospitals.com/know-your-pet/benadryl-diphenhydramine-for-dogs-and-cats), ASPCA (https://www.aspca.org/pet-care/animal-poison-control/people-foods-avoid-feeding-your-pets)',
                symptoms: 'sedation, dry mouth, urinary retention, agitation, seizures',
                mechanism: 'Histamine receptor antagonism with anticholinergic effects',
                type: 'medication'
            },
            'pseudoephedrine': {
                dog: {
                    toxic: true,
                    severity: 'high',
                    details: 'Sympathomimetic that causes severe cardiovascular and neurological effects'
                },
                cat: {
                    toxic: true,
                    severity: 'high',
                    details: 'Highly toxic - causes severe stimulant effects'
                },
                sources: 'Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/pseudoephedrine/), VCA Animal Hospitals (https://vcahospitals.com/know-your-pet/decongestant-poisoning-in-dogs), ASPCA (https://www.aspca.org/pet-care/animal-poison-control/people-foods-avoid-feeding-your-pets)',
                symptoms: 'hyperactivity, elevated heart rate, high blood pressure, hyperthermia, seizures',
                mechanism: 'Alpha and beta adrenergic stimulation',
                type: 'medication'
            },
            'naproxen': {
                dog: {
                    toxic: true,
                    severity: 'high',
                    details: 'NSAID with long half-life causing severe gastrointestinal and renal toxicity'
                },
                cat: {
                    toxic: true,
                    severity: 'high',
                    details: 'Extremely toxic - cats cannot metabolize NSAIDs effectively'
                },
                sources: 'Pet Poison Helpline (https://www.petpoisonhelpline.com/poison/naproxen/), VCA Animal Hospitals (https://vcahospitals.com/know-your-pet/nsaid-toxicity-in-dogs-and-cats), AVMA (https://www.avma.org/resources-tools/pet-owners/petcare/aspirin-and-other-nsaids)',
                symptoms: 'vomiting, diarrhea, kidney failure, liver damage, neurological signs',
                mechanism: 'COX enzyme inhibition causing GI ulceration and renal toxicity',
                type: 'medication'
            },
            'unknown': {
                general: {
                    toxic: null,
                    severity: 'unknown',
                    details: 'Insufficient data available for this ingredient - consult your veterinarian immediately'
                },
                sources: 'For unknown ingredients, consult ASPCA Animal Poison Control (https://www.aspca.org/pet-care/animal-poison-control) or Pet Poison Helpline (https://www.petpoisonhelpline.com/)',
                symptoms: 'unknown - monitor for any changes in behavior, appetite, or health',
                mechanism: 'requires veterinary assessment and research',
                type: 'unknown'
            }
        };
    }
}

// Risk Analysis Agent - Categorizes ingredients by risk level
class RiskAnalysisAgent {
    async analyze(researchData, petType) {
        console.log(`Risk Analysis Agent: Analyzing risk for ${researchData.ingredient}...`);
        await this.delay(200);

        const toxicityData = researchData.toxicityData;
        
        if (!toxicityData.toxic) {
            return 'no';
        }

        switch (toxicityData.severity) {
            case 'high':
                return 'high';
            case 'medium':
                return 'medium';
            case 'low':
                return 'low';
            default:
                return 'medium'; // Default to medium risk for unknown severity
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Fact Checker Agent - Validates research findings
class FactCheckerAgent {
    async validate(researchData, riskLevel) {
        console.log(`Fact Checker Agent: Validating findings for ${researchData.ingredient}...`);
        await this.delay(150);

        // Simulate fact-checking by adding confidence scores
        return {
            ...researchData,
            validated: true,
            confidence: this.calculateConfidence(researchData),
            crossReferencedSources: true
        };
    }

    calculateConfidence(data) {
        // Simulate confidence calculation based on source quality
        if (data.sources.includes('ASPCA') || data.sources.includes('AVMA')) {
            return 'high';
        } else if (data.sources.includes('Veterinary')) {
            return 'medium';
        }
        return 'low';
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Formatter Agent - Structures final output
class FormatterAgent {
    async format(ingredient, validatedData, riskLevel) {
        console.log(`Formatter Agent: Formatting results for ${ingredient}...`);
        await this.delay(100);

        return {
            name: ingredient,
            riskLevel: riskLevel,
            justification: this.generateJustification(validatedData, riskLevel),
            sources: validatedData.sources
        };
    }

    generateJustification(data, riskLevel) {
        const toxicityData = data.toxicityData;
        
        if (riskLevel === 'no') {
            return `${this.capitalizeFirst(data.ingredient)} is generally safe for ${data.petType}s. ${toxicityData.details}`;
        }

        const riskDescriptions = {
            'high': 'poses a serious threat and can be life-threatening',
            'medium': 'can cause significant health problems',
            'low': 'may cause mild adverse reactions'
        };

        let justification = `${this.capitalizeFirst(data.ingredient)} ${riskDescriptions[riskLevel]} for ${data.petType}s. ${toxicityData.details}`;
        
        if (data.symptoms && data.symptoms !== 'none' && data.symptoms !== 'unknown') {
            justification += ` Symptoms may include: ${data.symptoms}.`;
        }
        
        if (data.mechanism && data.mechanism !== 'requires further research') {
            justification += ` Mechanism: ${data.mechanism}.`;
        }
        
        return justification;
    }

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PetIngredientChecker();
});
