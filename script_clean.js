// Pet Ingredient Safety Checker - Frontend JavaScript (Backend API Version)

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
                                ${ingredient.cached ? '<div class="cached-indicator">📋 Cached Result</div>' : '<div class="live-indicator">🔍 Live Research</div>'}
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

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PetIngredientChecker();
});
