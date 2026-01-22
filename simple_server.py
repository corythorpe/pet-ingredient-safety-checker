#!/usr/bin/env python3
"""
Simple test server for Pet Ingredient Safety Checker
Tests the web interface with mock backend responses
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.parse
import os
from datetime import datetime

class PetSafetyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='.', **kwargs)
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_file('templates/index.html', 'text/html')
        elif self.path.startswith('/static/'):
            # Serve static files
            file_path = self.path[1:]  # Remove leading slash
            if file_path.endswith('.css'):
                self.serve_file(file_path, 'text/css')
            elif file_path.endswith('.js'):
                self.serve_file(file_path, 'application/javascript')
            else:
                self.send_error(404)
        elif self.path == '/api/health':
            self.send_json_response({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'agents': {
                    'research_agent': 'active (mock)',
                    'risk_analysis_agent': 'active (mock)',
                    'fact_checker_agent': 'active (mock)',
                    'formatter_agent': 'active (mock)'
                }
            })
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/evaluate':
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                ingredients = data.get('ingredients', [])
                pet_type = data.get('pet_type', 'cat')
                category = data.get('category', 'mixed')
                
                # Mock response with realistic data
                mock_results = self.generate_mock_results(ingredients, pet_type, 'mixed')
                
                self.send_json_response({
                    'success': True,
                    'results': mock_results,
                    'pet_type': pet_type,
                    'category': 'mixed',
                    'processed_at': datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                self.send_json_response({
                    'success': False,
                    'error': f'Error processing request: {str(e)}'
                }, status=500)
        else:
            self.send_error(404)
    
    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Content-length', len(content.encode('utf-8')))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404)
    
    def send_json_response(self, data, status=200):
        response = json.dumps(data, indent=2)
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-length', len(response.encode('utf-8')))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
    
    def generate_mock_results(self, ingredients, pet_type, category):
        """Generate realistic mock results for testing"""
        results = {'high': [], 'medium': [], 'low': [], 'no': []}
        
        # Known ingredient classifications
        ingredient_data = {
            'chocolate': {
                'risk': 'high',
                'justification': f'Chocolate poses a serious threat and can be life-threatening for {pet_type}s. Contains theobromine which is toxic to pets. Symptoms may include: vomiting, diarrhea, increased heart rate, seizures.',
                'confidence': 9
            },
            'onion': {
                'risk': 'high',
                'justification': f'Onion poses a serious threat and can be life-threatening for {pet_type}s. Contains compounds that damage red blood cells. Symptoms may include: weakness, vomiting, breathing problems, pale gums.',
                'confidence': 9
            },
            'garlic': {
                'risk': 'medium',
                'justification': f'Garlic can cause significant health problems for {pet_type}s. Contains compounds similar to onions but in lower concentrations. Symptoms may include: gastrointestinal upset, weakness.',
                'confidence': 8
            },
            'grapes': {
                'risk': 'high',
                'justification': f'Grapes pose a serious threat and can be life-threatening for {pet_type}s. Can cause kidney failure. Symptoms may include: vomiting, diarrhea, lethargy, loss of appetite.',
                'confidence': 9
            },
            'raisins': {
                'risk': 'high',
                'justification': f'Raisins pose a serious threat and can be life-threatening for {pet_type}s. Can cause kidney failure similar to grapes. Symptoms may include: vomiting, diarrhea, lethargy.',
                'confidence': 9
            },
            'ibuprofen': {
                'risk': 'high',
                'justification': f'Ibuprofen poses a serious threat and can be life-threatening for {pet_type}s. NSAID medication toxic to pets. Symptoms may include: vomiting, diarrhea, kidney failure, seizures.',
                'confidence': 10
            },
            'acetaminophen': {
                'risk': 'high',
                'justification': f'Acetaminophen poses a serious threat and can be life-threatening for {pet_type}s. Extremely toxic, especially to cats. Symptoms may include: difficulty breathing, swelling, liver damage.',
                'confidence': 10
            },
            'aspirin': {
                'risk': 'medium',
                'justification': f'Aspirin can cause significant health problems for {pet_type}s. Can cause gastrointestinal and bleeding issues. Symptoms may include: vomiting, diarrhea, loss of appetite.',
                'confidence': 8
            },
            'chicken': {
                'risk': 'no',
                'justification': f'Chicken is generally safe for {pet_type}s. Safe protein source for pets when cooked properly without seasoning.',
                'confidence': 9
            },
            'rice': {
                'risk': 'no',
                'justification': f'Rice is generally safe for {pet_type}s. Safe carbohydrate source that is easily digestible.',
                'confidence': 9
            },
            'beef': {
                'risk': 'no',
                'justification': f'Beef is generally safe for {pet_type}s. Good protein source when cooked properly without seasoning.',
                'confidence': 8
            },
            'fish': {
                'risk': 'no',
                'justification': f'Fish is generally safe for {pet_type}s. Excellent protein source, ensure it\'s cooked and boneless.',
                'confidence': 8
            },
            'carrots': {
                'risk': 'no',
                'justification': f'Carrots are generally safe for {pet_type}s. Good source of vitamins and fiber when given in moderation.',
                'confidence': 8
            },
            'sweet potato': {
                'risk': 'no',
                'justification': f'Sweet potato is generally safe for {pet_type}s. Nutritious vegetable that provides vitamins and fiber.',
                'confidence': 8
            }
        }
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            
            if ingredient_lower in ingredient_data:
                data = ingredient_data[ingredient_lower]
                risk_level = data['risk']
            else:
                # Unknown ingredient - default to medium risk
                risk_level = 'medium'
                data = {
                    'justification': f'{ingredient.capitalize()} requires veterinary assessment for {pet_type}s. Insufficient data available - consult your veterinarian before giving this to your pet.',
                    'confidence': 3
                }
            
            result = {
                'name': ingredient,
                'risk_level': risk_level,
                'justification': data['justification'],
                'sources': 'ASPCA Animal Poison Control, Pet Poison Helpline, VCA Hospitals',
                'confidence_score': data['confidence'],
                'cached': False,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            results[risk_level].append(result)
        
        return results

def start_server():
    """Start the simple test server"""
    port = 5000
    server_address = ('', port)
    
    print("🐾 Pet Ingredient Safety Checker - Test Server")
    print("=" * 50)
    print(f"🚀 Starting test server on port {port}...")
    print(f"📱 Open your browser to: http://localhost:{port}")
    print("🧪 This is a test server with mock responses")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        httpd = HTTPServer(server_address, PetSafetyHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        httpd.server_close()

if __name__ == '__main__':
    start_server()
