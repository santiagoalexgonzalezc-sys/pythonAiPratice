from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Create a Flask application instance
# Flask is a micro web framework for Python
app = Flask(__name__)

# Enable CORS (Cross-Origin Resource Sharing)
# This allows our HTML frontend to communicate with the Python backend
# even if they're on different ports or domains
CORS(app)

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
        
        # For now, we'll just echo the message back
        # We'll replace this with AI integration in Phase 6
        bot_response = f"You said: {user_message}"
        
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
