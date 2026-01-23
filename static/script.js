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
        
        // Add Enter key support for textarea
        this.ingredientsTextarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault(); // Prevent new line
                if (!this.evaluateBtn.disabled) {
                    this.handleEvaluate();
                }
            }
        });
    }

    async handleEvaluate() {
        const ingredients = this.parseIngredients(this.ingredientsTextarea.value);
        const petType = this.petTypeSelect.value;

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
                    category: 'mixed'  // Always use mixed category
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displayResults(data.results, petType);
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
        // Advanced parsing to extract ingredients from any text format
        const knownIngredients = [
            // Dangerous foods
            'chocolate', 'onion', 'onions', 'garlic', 'grapes', 'raisins', 'xylitol',
            'avocado', 'macadamia nuts', 'macadamia', 'walnuts', 'almonds', 'nuts',
            'caffeine', 'coffee', 'tea', 'alcohol', 'beer', 'wine', 'hops',
            
            // Common medications
            'ibuprofen', 'acetaminophen', 'aspirin', 'tylenol', 'advil', 'motrin',
            'naproxen', 'aleve', 'paracetamol', 'codeine', 'tramadol',
            
            // Safe foods
            'chicken', 'rice', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'turkey',
            'carrots', 'peas', 'sweet potato', 'potato', 'pumpkin', 'spinach',
            'broccoli', 'green beans', 'blueberries', 'apples', 'bananas',
            
            // Dairy and others
            'milk', 'cheese', 'yogurt', 'butter', 'eggs', 'bread', 'yeast',
            'salt', 'sugar', 'honey', 'corn', 'wheat', 'soy', 'dairy'
        ];
        
        const foundIngredients = new Set();
        const textLower = text.toLowerCase();
        
        // Method 1: Find known ingredients by substring matching
        knownIngredients.forEach(ingredient => {
            // Use word boundaries to avoid partial matches
            const regex = new RegExp(`\\b${ingredient.replace(/\s+/g, '\\s+')}\\b`, 'i');
            if (regex.test(textLower)) {
                foundIngredients.add(ingredient);
            }
        });
        
        // Method 2: Parse by common separators and clean up
        const separatorParsed = text
            .split(/[,\n;•\-\*\d+\.\)\(]/) // Split on various separators and list markers
            .map(item => {
                // Clean up the item
                return item
                    .replace(/\d+\s*(mg|g|ml|oz|lbs?|cups?|tbsp|tsp|tablets?|capsules?|pills?)/gi, '') // Remove measurements
                    .replace(/\b(with|and|or|plus|contains?|including?)\b/gi, ' ') // Remove connecting words
                    .replace(/[^\w\s]/g, ' ') // Remove special characters
                    .trim()
                    .toLowerCase();
            })
            .filter(item => item.length > 2 && item.length < 30) // Reasonable length
            .filter(item => !/^\d+$/.test(item)) // Remove pure numbers
            .filter(item => !/(the|and|or|with|for|from|this|that|these|those|very|much|many|some|any|all)/.test(item)); // Remove common words
        
        separatorParsed.forEach(ingredient => {
            if (ingredient.trim()) {
                foundIngredients.add(ingredient.trim());
            }
        });
        
        // Method 3: Look for ingredient patterns in natural language
        const ingredientPatterns = [
            /(?:contains?|includes?|has|with)\s+([a-zA-Z\s]{3,20})(?:\s|,|$)/gi,
            /(?:made with|contains?)\s+([a-zA-Z\s]{3,20})(?:\s|,|$)/gi,
            /([a-zA-Z\s]{3,20})\s+(?:extract|powder|oil|supplement)/gi
        ];
        
        ingredientPatterns.forEach(pattern => {
            let match;
            while ((match = pattern.exec(text)) !== null) {
                const ingredient = match[1].trim().toLowerCase();
                if (ingredient.length > 2 && ingredient.length < 25) {
                    foundIngredients.add(ingredient);
                }
            }
        });
        
        return Array.from(foundIngredients).filter(ingredient => ingredient.length > 1);
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

    displayResults(results, petType) {
        this.inputSection.style.display = 'none';
        this.resultsSection.style.display = 'block';

        const petEmoji = petType === 'cat' ? '🐱' : '🐕';
        
        const resultsHeader = this.resultsSection.querySelector('h2');
        resultsHeader.textContent = `${petEmoji} 🔍 Ingredient Safety Assessment for ${petType.charAt(0).toUpperCase() + petType.slice(1)}s`;

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
                                    <strong>Sources:</strong> ${this.makeUrlsClickable(ingredient.sources)}
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

    makeUrlsClickable(sources) {
        // Handle both string and array sources
        if (Array.isArray(sources)) {
            return sources.map(source => {
                // Ensure source is a string
                const sourceStr = String(source || '');
                
                // Check if source contains a URL
                const urlMatch = sourceStr.match(/(https?:\/\/[^\s,)]+)/);
                if (urlMatch) {
                    const url = urlMatch[0];
                    const cleanUrl = url.replace(/[.,;:!?)]$/, '');
                    const description = sourceStr.replace(url, '').trim().replace(/^[:\-\s]+|[:\-\s]+$/g, '');
                    return `<a href="${cleanUrl}" target="_blank" rel="noopener noreferrer" class="source-link">${description || cleanUrl}</a>`;
                }
                return sourceStr;
            }).join('<br>');
        } else if (typeof sources === 'string') {
            // Handle string sources (legacy format)
            const urlRegex = /(https?:\/\/[^\s,)]+)/g;
            return sources.replace(urlRegex, (url) => {
                const cleanUrl = url.replace(/[.,;:!?)]$/, '');
                const trailingPunct = url.slice(cleanUrl.length);
                return `<a href="${cleanUrl}" target="_blank" rel="noopener noreferrer" class="source-link">${cleanUrl}</a>${trailingPunct}`;
            });
        } else {
            // Handle any other type by converting to string
            return String(sources || 'No sources available');
        }
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
    
    // Initialize dropdown functionality
    const dropdownBtn = document.querySelector('.dropdown-btn');
    const dropdownContent = document.querySelector('.dropdown-content');
    
    if (dropdownBtn && dropdownContent) {
        // Toggle dropdown on button click
        dropdownBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isVisible = dropdownContent.style.display === 'block';
            dropdownContent.style.display = isVisible ? 'none' : 'block';
            
            // Update arrow direction
            const arrow = dropdownBtn.querySelector('span:last-child');
            if (arrow) {
                arrow.textContent = isVisible ? '▼' : '▲';
            }
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            dropdownContent.style.display = 'none';
            const arrow = dropdownBtn.querySelector('span:last-child');
            if (arrow) {
                arrow.textContent = '▼';
            }
        });
        
        // Add hover effects to dropdown items
        const dropdownItems = dropdownContent.querySelectorAll('a');
        dropdownItems.forEach(item => {
            item.addEventListener('mouseenter', () => {
                item.style.background = '#f8f9fa';
            });
            item.addEventListener('mouseleave', () => {
                item.style.background = 'white';
            });
        });
        
        // Add hover effect to dropdown button
        dropdownBtn.addEventListener('mouseenter', () => {
            dropdownBtn.style.background = '#e9ecef';
            dropdownBtn.style.borderColor = '#adb5bd';
        });
        dropdownBtn.addEventListener('mouseleave', () => {
            dropdownBtn.style.background = '#f8f9fa';
            dropdownBtn.style.borderColor = '#dee2e6';
        });
    }
});
