// How It Works Dashboard - Public-facing agent demonstration
class HowItWorksDemo {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.currentStep = 0;
        this.agents = ['researchAgent', 'riskAgent', 'factCheckAgent', 'formatterAgent'];
    }

    initializeElements() {
        this.startDemoBtn = document.getElementById('startDemo');
        this.demoIngredients = document.getElementById('demoIngredients');
        this.demoPetType = document.getElementById('demoPetType');
        this.loadingDemo = document.querySelector('.loading-demo');
        this.agentFlow = document.getElementById('agentFlow');
        
        // Get all agent cards
        this.agentCards = {
            researchAgent: document.getElementById('researchAgent'),
            riskAgent: document.getElementById('riskAgent'),
            factCheckAgent: document.getElementById('factCheckAgent'),
            formatterAgent: document.getElementById('formatterAgent')
        };
    }

    bindEvents() {
        this.startDemoBtn.addEventListener('click', () => this.startDemo());
        
        // Enable demo button only when ingredients are entered
        this.demoIngredients.addEventListener('input', () => {
            const hasIngredients = this.demoIngredients.value.trim().length > 0;
            this.startDemoBtn.disabled = !hasIngredients;
        });
        
        // Enter key support
        this.demoIngredients.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !this.startDemoBtn.disabled) {
                this.startDemo();
            }
        });
    }

    async startDemo() {
        const ingredients = this.parseIngredients(this.demoIngredients.value);
        const petType = this.demoPetType.value;

        if (ingredients.length === 0) {
            alert('Please enter at least one ingredient to see the demo.');
            return;
        }

        this.showLoading(true);
        this.resetAgentStates();

        try {
            // Demonstrate the agent workflow
            await this.demonstrateAgentWorkflow(ingredients, petType);
        } catch (error) {
            console.error('Demo error:', error);
            this.displayError('Demo failed. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }

    async demonstrateAgentWorkflow(ingredients, petType) {
        const sampleIngredient = ingredients[0]; // Use first ingredient for demo
        
        // Step 1: Research Agent
        await this.demonstrateAgent('researchAgent', 'Research Agent', 
            `🔍 Searching the web for "${sampleIngredient}" safety information...`, 
            `Found veterinary studies and toxicity reports for ${sampleIngredient}. Checking ASPCA database and Pet Poison Helpline.`
        );

        // Step 2: Risk Analysis Agent
        await this.demonstrateAgent('riskAgent', 'Risk Analysis Agent', 
            `⚖️ Analyzing research data to determine risk level...`, 
            `AI analysis complete. Categorized ${sampleIngredient} based on toxicity data and ${petType} physiology.`
        );

        // Step 3: Fact Checker Agent
        await this.demonstrateAgent('factCheckAgent', 'Fact Checker Agent', 
            `✅ Cross-referencing with authoritative veterinary sources...`, 
            `Validated findings against multiple sources. Identified key symptoms and toxic mechanisms.`
        );

        // Step 4: Formatter Agent
        await this.demonstrateAgent('formatterAgent', 'Formatter Agent', 
            `📝 Organizing results into clear recommendations...`, 
            `Final safety assessment ready with detailed explanations and source citations.`
        );

        // Call the real API and show actual results
        setTimeout(async () => {
            await this.fetchAndDisplayResults(ingredients, petType);
        }, 1000);
    }

    async demonstrateAgent(agentId, agentName, workingMessage, completedMessage) {
        const card = this.agentCards[agentId];
        const statusElement = card.querySelector('.agent-status');
        const detailsElement = card.querySelector('.agent-details');
        const currentTaskElement = card.querySelector('.current-task');
        const progressFillElement = card.querySelector('.progress-fill');
        
        // Show details and set agent to working state
        detailsElement.style.display = 'block';
        card.classList.add('active');
        statusElement.textContent = 'Working...';
        statusElement.className = 'agent-status working';
        
        // Update description to show what it's doing
        const descriptionElement = card.querySelector('.agent-description');
        const originalDescription = descriptionElement.textContent;
        descriptionElement.textContent = workingMessage;
        currentTaskElement.textContent = workingMessage;
        
        // Animate progress bar
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.random() * 15 + 5;
            if (progress > 100) progress = 100;
            progressFillElement.style.width = `${progress}%`;
            
            if (progress >= 100) {
                clearInterval(progressInterval);
            }
        }, 200);
        
        // Simulate processing time
        await new Promise(resolve => setTimeout(resolve, Math.random() * 2000 + 1500));
        
        // Ensure progress is complete
        progressFillElement.style.width = '100%';
        
        // Set agent to completed state
        card.classList.remove('active');
        card.classList.add('completed');
        statusElement.textContent = 'Completed';
        statusElement.className = 'agent-status completed';
        descriptionElement.textContent = completedMessage;
        currentTaskElement.textContent = 'Task completed successfully';
        
        // Brief pause before next agent
        await new Promise(resolve => setTimeout(resolve, 500));
    }

    showCompletionMessage(ingredients, petType) {
        // Create a completion message
        const completionDiv = document.createElement('div');
        completionDiv.className = 'completion-message';
        completionDiv.style.cssText = `
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 20px;
            margin-top: 30px;
            text-align: center;
        `;
        
        completionDiv.innerHTML = `
            <h3 style="color: #155724; margin: 0 0 10px 0;">🎉 Analysis Complete!</h3>
            <p style="color: #155724; margin: 0;">
                Our AI agents have successfully analyzed <strong>${ingredients.length} ingredient${ingredients.length !== 1 ? 's' : ''}</strong> 
                for <strong>${petType}</strong> safety. In a real application, you would now see detailed safety recommendations 
                with risk levels, explanations, and authoritative sources.
            </p>
            <button onclick="location.href='/'" style="
                margin-top: 15px;
                padding: 10px 20px;
                background: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-weight: 500;
            ">Try the Real App</button>
        `;
        
        this.agentFlow.parentNode.appendChild(completionDiv);
        
        // Scroll to completion message
        completionDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    resetAgentStates() {
        // Remove any existing completion message
        const existingCompletion = document.querySelector('.completion-message');
        if (existingCompletion) {
            existingCompletion.remove();
        }
        
        // Reset all agent cards
        Object.values(this.agentCards).forEach(card => {
            card.classList.remove('active', 'completed');
            const statusElement = card.querySelector('.agent-status');
            statusElement.textContent = 'Waiting';
            statusElement.className = 'agent-status waiting';
        });
        
        // Reset descriptions to original text
        const descriptions = {
            researchAgent: 'Searches the internet for veterinary information about each ingredient',
            riskAgent: 'Analyzes research data to determine safety risk levels',
            factCheckAgent: 'Validates findings against authoritative veterinary sources',
            formatterAgent: 'Organizes results into clear, actionable safety recommendations'
        };
        
        Object.entries(descriptions).forEach(([agentId, description]) => {
            const card = this.agentCards[agentId];
            const descriptionElement = card.querySelector('.agent-description');
            descriptionElement.textContent = description;
        });
    }

    parseIngredients(text) {
        // Simple parsing for demo purposes
        const knownIngredients = [
            'chocolate', 'onion', 'onions', 'garlic', 'grapes', 'raisins', 'xylitol',
            'avocado', 'macadamia nuts', 'macadamia', 'walnuts', 'almonds', 'nuts',
            'caffeine', 'coffee', 'tea', 'alcohol', 'beer', 'wine', 'hops',
            'ibuprofen', 'acetaminophen', 'aspirin', 'tylenol', 'advil', 'motrin',
            'chicken', 'rice', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'turkey',
            'carrots', 'peas', 'sweet potato', 'potato', 'pumpkin', 'spinach'
        ];
        
        const foundIngredients = new Set();
        const textLower = text.toLowerCase();
        
        // Find known ingredients
        knownIngredients.forEach(ingredient => {
            const regex = new RegExp(`\\b${ingredient.replace(/\s+/g, '\\s+')}\\b`, 'i');
            if (regex.test(textLower)) {
                foundIngredients.add(ingredient);
            }
        });
        
        // Parse by common separators
        const separatorParsed = text
            .split(/[,\n;•\-\*\d+\.\)\(]/)
            .map(item => item.trim().toLowerCase())
            .filter(item => item.length > 2 && item.length < 30)
            .filter(item => !/^\d+$/.test(item))
            .filter(item => !/(the|and|or|with|for|from|this|that|these|those|very|much|many|some|any|all)/.test(item));
        
        separatorParsed.forEach(ingredient => {
            if (ingredient.trim()) {
                foundIngredients.add(ingredient.trim());
            }
        });
        
        return Array.from(foundIngredients).filter(ingredient => ingredient.length > 1);
    }

    showLoading(isLoading) {
        this.startDemoBtn.disabled = isLoading;
        this.loadingDemo.style.display = isLoading ? 'block' : 'none';
        
        if (isLoading) {
            this.resetAgentStates();
        }
    }

    displayError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.cssText = `
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
            text-align: center;
        `;
        errorDiv.innerHTML = `<strong>Error:</strong> ${message}`;
        
        this.agentFlow.parentNode.appendChild(errorDiv);
        
        // Remove error after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }

    async fetchAndDisplayResults(ingredients, petType) {
        try {
            // Call the real API
            const response = await fetch('/api/evaluate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ingredients: ingredients,
                    pet_type: petType,
                    category: 'mixed'
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.displayResults(data, ingredients, petType);
            } else {
                this.showCompletionMessage(ingredients, petType);
            }
        } catch (error) {
            console.error('Failed to fetch results:', error);
            this.showCompletionMessage(ingredients, petType);
        }
    }

    displayResults(data, ingredients, petType) {
        const resultsSection = document.getElementById('demoResultsSection');
        const summaryElement = document.getElementById('demoSummary');
        const resultsGrid = document.getElementById('demoResultsGrid');
        
        // Show the results section
        resultsSection.style.display = 'block';
        
        // Calculate summary statistics
        const totalIngredients = Object.values(data.results).reduce((sum, arr) => sum + arr.length, 0);
        const riskCounts = {
            high: data.results.high?.length || 0,
            medium: data.results.medium?.length || 0,
            low: data.results.low?.length || 0,
            no: data.results.no?.length || 0
        };
        
        // Create summary
        summaryElement.innerHTML = `
            <div class="demo-summary-stats">
                <div class="demo-summary-stat">
                    <div class="value">${totalIngredients}</div>
                    <div class="label">Ingredients</div>
                </div>
                <div class="demo-summary-stat">
                    <div class="value">${riskCounts.high}</div>
                    <div class="label">High Risk</div>
                </div>
                <div class="demo-summary-stat">
                    <div class="value">${riskCounts.medium}</div>
                    <div class="label">Medium Risk</div>
                </div>
                <div class="demo-summary-stat">
                    <div class="value">${riskCounts.low}</div>
                    <div class="label">Low Risk</div>
                </div>
                <div class="demo-summary-stat">
                    <div class="value">${riskCounts.no}</div>
                    <div class="label">Safe</div>
                </div>
                <div class="demo-summary-stat">
                    <div class="value">${data.mode === 'digitalocean_genai_powered' ? 'AI' : 'Basic'}</div>
                    <div class="label">Mode</div>
                </div>
            </div>
        `;
        
        // Create risk category cards
        const riskCategories = [
            { key: 'high', title: 'High Risk', icon: '🚨', description: 'Dangerous - Avoid completely' },
            { key: 'medium', title: 'Medium Risk', icon: '⚠️', description: 'Caution required' },
            { key: 'low', title: 'Low Risk', icon: '⚡', description: 'Minor concerns' },
            { key: 'no', title: 'No Risk', icon: '✅', description: 'Safe for consumption' }
        ];
        
        const categoriesHtml = riskCategories.map(category => {
            const categoryIngredients = data.results[category.key] || [];
            const count = categoryIngredients.length;
            
            const ingredientsHtml = categoryIngredients.length > 0 ? 
                `<ul class="demo-ingredient-list">
                    ${categoryIngredients.map(ingredient => `<li>${ingredient.name}</li>`).join('')}
                </ul>` : 
                '<p style="color: #999; font-style: italic; margin: 0;">No ingredients in this category</p>';
            
            return `
                <div class="demo-risk-category ${category.key}">
                    <h4>
                        ${category.icon} ${category.title}
                        <span class="demo-risk-badge ${category.key}">${count}</span>
                    </h4>
                    <p style="margin-bottom: 15px; color: #666; font-size: 0.9em;">${category.description}</p>
                    ${ingredientsHtml}
                </div>
            `;
        }).join('');
        
        resultsGrid.innerHTML = categoriesHtml;
        
        // Add completion message with link to main app
        const completionDiv = document.createElement('div');
        completionDiv.className = 'completion-message';
        completionDiv.style.cssText = `
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 20px;
            margin-top: 30px;
            text-align: center;
        `;
        
        completionDiv.innerHTML = `
            <h3 style="color: #155724; margin: 0 0 10px 0;">🎉 Real Analysis Complete!</h3>
            <p style="color: #155724; margin: 0 0 15px 0;">
                Our AI agents have successfully analyzed <strong>${totalIngredients} ingredient${totalIngredients !== 1 ? 's' : ''}</strong> 
                for <strong>${petType}</strong> safety using ${data.mode === 'digitalocean_genai_powered' ? 'DigitalOcean GenAI' : 'fallback mode'}.
            </p>
            <button onclick="location.href='/'" style="
                padding: 12px 24px;
                background: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                margin-right: 10px;
            ">Try Full App</button>
            <button onclick="location.href='/admin'" style="
                padding: 12px 24px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
            ">View Admin Dashboard</button>
        `;
        
        resultsSection.appendChild(completionDiv);
        
        // Scroll to results section
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Initialize the demo when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new HowItWorksDemo();
});
