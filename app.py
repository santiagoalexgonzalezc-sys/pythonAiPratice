from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os

# Create a Flask application instance
# Flask is a micro web framework for Python
app = Flask(__name__)

# Enable CORS (Cross-Origin Resource Sharing)
# This allows our HTML frontend to communicate with the Python backend
# even if they're on different ports or domains
CORS(app)

# Load the knowledge base from JSON file
# This file contains predefined questions and answers
def load_knowledge_base():
    try:
        # Get the directory where this script is located
        base_dir = os.path.dirname(os.path.abspath(__file__))
        knowledge_path = os.path.join(base_dir, 'knowledge_base.json')
        
        # Open and read the JSON file
        with open(knowledge_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: knowledge_base.json file not found")
        return {}
    except json.JSONDecodeError:
        print("Error: knowledge_base.json contains invalid JSON")
        return {}

# Load knowledge base when the app starts
knowledge_base = load_knowledge_base()

# Function to find the best response based on keywords
def find_response(user_message):
    # Convert message to lowercase for case-insensitive matching
    user_message_lower = user_message.lower()
    
    # Iterate through all categories in the knowledge base
    for category, data in knowledge_base.items():
        # Skip the default category (we'll use it as fallback)
        if category == 'default':
            continue
            
        # Check if any keyword from this category is in the user's message
        for keyword in data['keywords']:
            if keyword.lower() in user_message_lower:
                # Return the response for this category
                return data['response']
    
    # If no keywords matched, return the default response
    return knowledge_base.get('default', {}).get('response', "I'm not sure how to help with that.")

# Route decorator - this maps a URL to a Python function
# When someone visits the root URL '/', this function runs
@app.route('/')
def home():
    # render_template looks for HTML files in the 'templates' folder
    # This serves our chat interface to the user
    return render_template('index.html')

# This route handles chat messages from the frontend
# methods=['POST'] means this only accepts POST requests (for sending data)
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get the JSON data sent from the frontend
        data = request.json
        
        # Extract the user's message from the JSON data
        user_message = data.get('message', '')
        
        # Use the knowledge base to find the appropriate response
        bot_response = find_response(user_message)
        
        # Return the response as JSON
        # jsonify converts Python dictionaries to JSON format
        return jsonify({
            'response': bot_response
        })
        
    except Exception as e:
        # If something goes wrong, return an error message
        return jsonify({'error': str(e)}), 500

# This block runs only when the file is executed directly
# (not when imported as a module)
if __name__ == '__main__':
    # debug=True enables auto-reload when code changes
    # port=5000 specifies which port the server runs on
    app.run(debug=True, port=5000)
