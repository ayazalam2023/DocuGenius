import os
from flask import Flask, request, jsonify, render_template
import pytesseract
from PIL import Image
import PyPDF2

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

extracted_text = ""  # Store extracted text globally

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global extracted_text
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # For PDF file
    if file.filename.endswith('.pdf'):
        with open(file_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            extracted_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    else:  # For Image file (PNG, JPG, JPEG)
        extracted_text = pytesseract.image_to_string(Image.open(file_path))

    print(f"Extracted Text: {extracted_text}")  # Debugging print statement
    return jsonify({'message': 'Upload successful', 'text': extracted_text})

@app.route('/ask', methods=['POST'])
def answer_question():
    global extracted_text
    question = request.json.get('question')
    print(f"User Question: {question}")  # Debugging print statement

    if not extracted_text:
        return jsonify({'answer': "No text available. Please upload a document first."})

    if question.lower() in extracted_text.lower():
        answer = "Yes, this information is in the document."
    else:
        answer = "I couldn't find relevant information in the document."

    print(f"Answer: {answer}")  # Debugging print statement
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)
