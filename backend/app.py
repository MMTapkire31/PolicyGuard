from flask import Flask, request, jsonify   # Flask = web server, request = incoming data, jsonify = converts dict to JSON response
from flask_cors import CORS                  # Allows Chrome extension (different origin) to talk to Flask
from analyzer import analyze_policy          # Our own function — we'll build this next

app = Flask(__name__)   # Creates the Flask app
CORS(app)               # Enables cross-origin requests (Chrome extension needs this)

@app.route('/analyze', methods=['POST'])    # Listen for POST requests at /analyze
def analyze():
    data = request.get_json()               # Extract the JSON body sent by the extension
    text = data.get('text', '')             # Get the 'text' field; default to '' if missing

    if not text:                            # If no text was sent, return an error
        return jsonify({'error': 'No text provided'}), 400

    result = analyze_policy(text)           # Pass text to our DistilBERT function
    return jsonify(result)                  # Send the result back as JSON

if __name__ == '__main__':
    app.run(debug=True, port=5000)          # Run locally on port 5000