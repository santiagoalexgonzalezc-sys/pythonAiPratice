from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
import re  # Regular expressions module for pattern matching in math expressions

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

# Function to calculate math expressions programmatically
# This function acts as a calculator that can solve arithmetic and basic algebra problems
def calculate_math(user_message):
    """
    Detects and calculates math expressions in the user's message.
    
    This function implements a calculator that can:
    1. Solve basic arithmetic: addition (+), subtraction (-), multiplication (* or x), division (/ or ÷)
    2. Solve basic algebra equations: find the value of x in equations like x+5=10, 2x=10, x/2=5
    
    How it works:
    - Uses regular expressions (regex) to detect math patterns in the user's message
    - For arithmetic: extracts the expression, converts visual operators (x, ÷) to Python operators (*, /)
    - For algebra: parses the equation structure and solves for x using inverse operations
    - Returns a formatted string with the answer, or None if no math expression is found
    
    Args:
        user_message (str): The text message from the user that may contain a math problem
    
    Returns:
        str: A formatted answer string if math is detected, None otherwise
    
    Examples:
        "2+2" → "The answer is: 4"
        "x+5=10" → "If x + 5 = 10, then x = 5"
        "2x=10" → "If 2x = 10, then x = 5"
    """
    # Step 1: Preprocess the message
    # Remove all spaces and convert to lowercase for consistent pattern matching
    # This makes the pattern matching more flexible (e.g., "2 + 2" and "2+2" both work)
    message = user_message.replace(' ', '').lower()
    
    # Step 2: Try to detect and solve basic arithmetic expressions
    # Regex pattern explanation:
    # \d+ matches one or more digits (the first number)
    # [+\-\*\/x÷] matches any of these operators: +, -, *, /, x, ÷
    # \d+ matches one or more digits (the second number)
    # This captures patterns like "2+2", "10-5", "3x2", "10/2", "5÷2"
    arithmetic_pattern = r'(\d+[\+\-\*\/x÷]\d+)'
    match = re.search(arithmetic_pattern, message)
    
    if match:
        # Extract the matched expression (e.g., "2+2")
        expression = match.group(1)
        try:
            # Convert visual operators to Python operators
            # 'x' is commonly used for multiplication in casual writing, but Python uses '*'
            # '÷' is the division symbol, but Python uses '/'
            expression = expression.replace('x', '*').replace('÷', '/')
            
            # Evaluate the mathematical expression using Python's eval()
            # Note: In production, you'd want to use a safer method like ast.literal_eval
            # or a math expression parser for security reasons
            result = eval(expression)
            
            # Format the result nicely
            # If the result is a whole number (e.g., 4.0), convert it to an integer (4)
            # This makes the output cleaner and more natural
            if result == int(result):
                result = int(result)
            
            return f"The answer is: {result}"
        except:
            # If evaluation fails for any reason, return None to fall back to knowledge base
            return None
    
    # Step 3: Try to detect and solve basic algebra equations
    # Regex pattern explanation:
    # This complex pattern matches three types of algebra equations:
    # 1. x + 5 = 10 (x with operator and number equals result)
    # 2. 2x = 10 (coefficient times x equals result)
    # 3. x / 2 = 5 (x divided by number equals result)
    # The pattern uses groups (parentheses) to capture different parts of the equation
    algebra_pattern = r'x([+\-\*/÷])(\d+)\s*=\s*(\d+)|(\d+)x\s*=\s*(\d+)|x\s*/\s*(\d+)\s*=\s*(\d+)'
    match = re.search(algebra_pattern, user_message.lower())
    
    if match:
        try:
            # Case 1: Solve equations like "x + 5 = 10" or "x - 3 = 7"
            # Groups: 1=operator, 2=number, 3=result
            if match.group(1) and match.group(2) and match.group(3):
                operator = match.group(1)  # The operator (+, -, *, /)
                number = float(match.group(2))  # The number with x
                result = float(match.group(3))  # The result after the equals sign
                
                # Solve for x using inverse operations:
                # If x + 5 = 10, then x = 10 - 5 (subtract both sides by 5)
                # If x - 3 = 7, then x = 7 + 3 (add both sides by 3)
                # If x * 2 = 10, then x = 10 / 2 (divide both sides by 2)
                # If x / 2 = 5, then x = 5 * 2 (multiply both sides by 2)
                if operator == '+':
                    x = result - number
                elif operator == '-':
                    x = result + number
                elif operator == '*':
                    x = result / number
                elif operator == '/':
                    x = result * number
                
                # Format the result nicely (convert to int if whole number)
                if x == int(x):
                    x = int(x)
                return f"If x {operator} {number} = {result}, then x = {x}"
            
            # Case 2: Solve equations like "2x = 10" (coefficient times x)
            # Groups: 4=coefficient, 5=result
            elif match.group(4) and match.group(5):
                coefficient = float(match.group(4))  # The number multiplying x
                result = float(match.group(5))  # The result
                
                # To solve 2x = 10, divide both sides by 2: x = 10 / 2 = 5
                x = result / coefficient
                
                # Format the result nicely
                if x == int(x):
                    x = int(x)
                return f"If {coefficient}x = {result}, then x = {x}"
            
            # Case 3: Solve equations like "x / 2 = 5" (x divided by number)
            # Groups: 6=divisor, 7=result
            elif match.group(6) and match.group(7):
                divisor = float(match.group(6))  # The number dividing x
                result = float(match.group(7))  # The result
                
                # To solve x / 2 = 5, multiply both sides by 2: x = 5 * 2 = 10
                x = result * divisor
                
                # Format the result nicely
                if x == int(x):
                    x = int(x)
                return f"If x ÷ {divisor} = {result}, then x = {x}"
        except:
            # If solving fails for any reason, return None to fall back to knowledge base
            return None
    
    # Step 4: No math expression detected
    # Return None to signal that the message should be handled by the knowledge base
    return None

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
    """
    Main chat endpoint that processes user messages and returns bot responses.
    
    This function implements a two-tier response system:
    1. First tier: Check if the message contains a math expression and calculate it
    2. Second tier: If no math, search the knowledge base for matching keywords
    
    This hybrid approach allows the bot to:
    - Act as a calculator for math problems (dynamic, unlimited possibilities)
    - Act as a knowledge base for general questions (static, predefined responses)
    
    Request format (JSON):
        {
            "message": "user's message here"
        }
    
    Response format (JSON):
        {
            "response": "bot's response here"
        }
    
    Error response format (JSON):
        {
            "error": "error message here"
        }
    """
    try:
        # Step 1: Extract the user's message from the incoming JSON request
        # request.json contains the data sent by the frontend
        data = request.json
        
        # Get the 'message' field, default to empty string if not present
        user_message = data.get('message', '')
        
        # Step 2: Check if the message contains a math expression
        # This is the first tier of our response system
        # calculate_math() will return a result if math is detected, None otherwise
        math_result = calculate_math(user_message)
        
        if math_result:
            # Math expression detected and calculated successfully
            # Use the calculated result as the bot's response
            bot_response = math_result
        else:
            # No math expression found, fall back to knowledge base
            # This is the second tier of our response system
            # find_response() searches the JSON knowledge base for matching keywords
            bot_response = find_response(user_message)
        
        # Step 3: Return the response to the frontend
        # jsonify() converts the Python dictionary to JSON format
        # The frontend will receive this JSON and display it to the user
        return jsonify({
            'response': bot_response
        })
        
    except Exception as e:
        # Step 4: Error handling
        # If anything goes wrong (invalid JSON, missing fields, etc.)
        # Return an error response with HTTP status code 500 (Internal Server Error)
        # The frontend can display this error message to the user
        return jsonify({'error': str(e)}), 500

# This block runs only when the file is executed directly
# (not when imported as a module)
if __name__ == '__main__':
    # debug=True enables auto-reload when code changes
    # port=5000 specifies which port the server runs on
    app.run(debug=True, port=5000)
