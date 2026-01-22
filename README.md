# 🐾 Pet Ingredient Safety Checker

A comprehensive multi-agent application that evaluates the safety of both food and medication ingredients for cats and dogs.

## Features

- **Multi-Agent System**: Four specialized AI agents work together to research, analyze, fact-check, and format ingredient safety information
- **Dual Category Support**: Handles both food ingredients and medication ingredients
- **Pet-Specific Analysis**: Tailored risk assessments for cats and dogs
- **Professional Sources**: Uses official veterinary sources like ASPCA, AVMA, and Pet Poison Helpline
- **Risk Categorization**: Clear high/medium/low/no risk classifications
- **Detailed Justifications**: Each ingredient includes explanation, symptoms, and mechanism of action
- **Responsive Design**: Professional, veterinary-inspired interface

## Multi-Agent Architecture

### 1. Research Agent
- Searches knowledge base for ingredient safety data
- Gathers toxicity information from official veterinary sources
- Provides pet-specific toxicity data

### 2. Risk Analysis Agent
- Categorizes ingredients into risk levels based on severity
- Applies logical risk assessment criteria:
  - **High Risk**: Potential for death or life-threatening conditions
  - **Medium Risk**: Serious health complications, organ damage
  - **Low Risk**: Mild reactions, temporary discomfort
  - **No Risk**: Safe for consumption

### 3. Fact Checker Agent
- Validates research findings
- Cross-references multiple official sources
- Calculates confidence scores based on source quality

### 4. Formatter Agent
- Structures final output with justifications
- Includes symptoms and mechanism of action
- Cites authoritative sources

## Knowledge Base

### Food Ingredients
- Chocolate, onions, garlic, grapes, raisins
- Avocado, chicken, rice
- And more...

### Medication Ingredients
- NSAIDs (ibuprofen, naproxen, aspirin)
- Acetaminophen
- Xylitol, caffeine
- Antihistamines (diphenhydramine)
- Decongestants (pseudoephedrine)
- And more...

## Usage

1. **Select Pet Type**: Choose between cat (default) or dog
2. **Choose Category**: Select food ingredients, medication ingredients, or mixed
3. **Enter Ingredients**: List ingredients one per line or comma-separated
4. **Evaluate**: Click the evaluate button to process through the multi-agent system
5. **Review Results**: View categorized results with detailed justifications and sources

## Deployment

### Local Deployment
1. Clone or download the project files
2. Open `index.html` in a web browser
3. No server setup required - runs entirely in the browser

### Web Server Deployment
1. Upload all files to your web server
2. Ensure `index.html`, `styles.css`, and `script.js` are in the same directory
3. Access via your domain

## Files

- `index.html` - Main application interface
- `styles.css` - Professional styling with blue/green color palette
- `script.js` - Multi-agent system and application logic
- `README.md` - This documentation

## Important Disclaimers

⚠️ **This tool provides general guidance based on veterinary sources. Always consult your veterinarian for specific dietary advice and medication safety. Never give human medications to pets without veterinary approval.**

## Technical Details

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Architecture**: Object-oriented multi-agent system
- **Styling**: CSS custom properties, responsive design
- **Browser Support**: Modern browsers with ES6+ support

## Sources

All ingredient data is sourced from official veterinary organizations:
- ASPCA Animal Poison Control Center
- American Veterinary Medical Association (AVMA)
- Pet Poison Helpline
- FDA Center for Veterinary Medicine
- Veterinary toxicology journals and databases

---

**Created with professional veterinary guidance for pet safety education.**
