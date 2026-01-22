# 🐾 Pet Ingredient Safety Checker

A sophisticated multi-agent web application that helps pet owners determine the safety of ingredients for their cats and dogs. The system uses AI-powered agents to research, analyze, and provide detailed safety assessments with risk categorization and source citations.

## ✨ Features

### 🤖 Multi-Agent Architecture
- **Research Agent**: Searches official veterinary sources for ingredient safety data
- **Risk Analysis Agent**: Categorizes ingredients into risk levels (High/Medium/Low/No Risk)
- **Fact Checker Agent**: Validates and cross-references research findings
- **Formatter Agent**: Structures results for clear, readable output

### 🌐 Web Interface
- Clean, responsive design optimized for mobile and desktop
- Pet type selection (Cat/Dog)
- Ingredient category filtering (Food/Medication/Mixed)
- Real-time ingredient parsing from any text format
- Detailed results with justifications and source citations

### 🗄️ Smart Caching
- SQLite database for development, PostgreSQL for production
- 30-day cache expiration for research results
- Reduces API calls and improves response times

### 🔍 Comprehensive Analysis
- Risk level categorization with clear explanations
- Symptom descriptions and toxicity mechanisms
- Confidence scoring based on source quality
- Official veterinary source citations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (for AI analysis)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd petproject
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Start the application**
   ```bash
   python start_app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## 🏗️ Architecture

### Multi-Agent System Flow
```
User Input → Research Agent → Risk Analysis Agent → Fact Checker Agent → Formatter Agent → Results
```

### Components

#### Research Agent
- Generates targeted search queries for veterinary sources
- Scrapes official websites (ASPCA, Pet Poison Helpline, VCA Hospitals)
- Uses OpenAI GPT-4 for intelligent analysis of research data
- Implements fallback analysis for known dangerous ingredients

#### Risk Analysis Agent
- Maps research findings to standardized risk levels
- Applies consistent categorization criteria
- Handles edge cases and unknown ingredients

#### Fact Checker Agent
- Validates research findings for accuracy
- Adds metadata for traceability
- Cross-references multiple sources

#### Formatter Agent
- Generates human-readable justifications
- Structures data for frontend consumption
- Includes confidence scoring and source attribution

### Database Schema
```sql
CREATE TABLE ingredient_research (
    id UUID PRIMARY KEY,
    ingredient_name VARCHAR(255) NOT NULL,
    pet_type VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    research_hash VARCHAR(64) UNIQUE NOT NULL,
    toxicity_data TEXT NOT NULL,
    sources TEXT NOT NULL,
    symptoms TEXT,
    mechanism TEXT,
    risk_level VARCHAR(20) NOT NULL,
    confidence_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_validated BOOLEAN DEFAULT FALSE,
    validation_count INTEGER DEFAULT 0
);
```

## 🧪 Testing

### Run the test suite
```bash
python test_simple.py
```

This runs a comprehensive test of the multi-agent system using mock data to verify:
- Agent communication and data flow
- Risk categorization logic
- Result formatting
- Error handling

### Example Test Output
```
🐾 Pet Ingredient Safety Checker - Multi-Agent System Test
============================================================

🔬 Test Case 1: Dog - Food
Ingredients: chocolate, chicken, rice, onion

⚠️ HIGH RISK (2 ingredients):
  • chocolate - Contains theobromine which is toxic to pets
  • onion - Contains compounds that damage red blood cells

✅ NO RISK (2 ingredients):
  • chicken - Safe protein source for pets when cooked properly
  • rice - Safe carbohydrate source for pets
```

## 📁 Project Structure

```
petproject/
├── backend/
│   └── app.py              # Main Flask application with multi-agent system
├── static/
│   ├── script.js           # Frontend JavaScript
│   └── styles.css          # CSS styling
├── templates/
│   └── index.html          # Main HTML template
├── agents/                 # Individual agent implementations (legacy)
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
├── start_app.py           # Application startup script
├── test_simple.py         # Test suite for multi-agent system
├── Dockerfile             # Docker configuration
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI analysis | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///pet_safety.db` |
| `FLASK_ENV` | Flask environment | `development` |
| `PORT` | Server port | `5000` |
| `SECRET_KEY` | Flask secret key | `dev_secret_key_change_in_production` |

### Risk Level Criteria

- **High Risk**: Life-threatening, potential for death
- **Medium Risk**: Serious health complications, organ damage  
- **Low Risk**: Mild reactions, temporary discomfort
- **No Risk**: Generally safe for consumption

## 🌐 API Endpoints

### POST /api/evaluate
Evaluate ingredient safety for pets.

**Request Body:**
```json
{
  "ingredients": ["chocolate", "chicken", "rice"],
  "pet_type": "dog",
  "category": "food"
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "high": [
      {
        "name": "chocolate",
        "risk_level": "high",
        "justification": "Chocolate poses a serious threat...",
        "sources": "ASPCA Animal Poison Control, Pet Poison Helpline",
        "confidence_score": 9,
        "cached": false
      }
    ],
    "medium": [],
    "low": [],
    "no": [...]
  },
  "pet_type": "dog",
  "category": "food",
  "processed_at": "2024-01-15T10:30:00Z"
}
```

### GET /api/health
Health check endpoint.

### GET /api/cache/stats
Cache statistics and performance metrics.

## 🚀 Deployment

### Docker Deployment
```bash
docker build -t pet-safety-checker .
docker run -p 5000:5000 -e OPENAI_API_KEY=your_key pet-safety-checker
```

### DigitalOcean App Platform
1. Connect your repository
2. Set environment variables in the control panel
3. Deploy with automatic scaling

### Production Considerations
- Use PostgreSQL for the database
- Set up Redis for enhanced caching
- Configure proper logging and monitoring
- Use HTTPS with SSL certificates
- Set strong secret keys

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This application is for informational purposes only and should not replace professional veterinary advice. Always consult with a qualified veterinarian before giving any new food or medication to your pet.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the test suite: `python test_simple.py`
2. Review the logs for error messages
3. Ensure all environment variables are set correctly
4. Verify your OpenAI API key is valid

## 🔮 Future Enhancements

- [ ] Integration with additional veterinary databases
- [ ] Mobile app development
- [ ] Multi-language support
- [ ] Dosage calculations for medications
- [ ] Emergency contact integration
- [ ] Veterinarian consultation booking
- [ ] Pet profile management
- [ ] Ingredient barcode scanning
