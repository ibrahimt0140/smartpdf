# SmartPDF

SmartPDF is an AI-powered PDF summarization web application built with Flask. It allows users to upload PDF files, extract text from both text-based and scanned PDFs, and generate summaries using Gemini AI.

## Features

- Upload PDF files through a simple web interface
- Extract text from text-based PDF files
- Extract text from scanned or image-based PDF files using OCR
- Generate AI-powered summaries with Gemini API
- Provide local fallback summarization when the AI service is unavailable
- Display extracted text and generated summary
- Simple and responsive Bootstrap-based user interface

## Technologies Used

- Python
- Flask
- Gemini API
- pdfplumber
- PyMuPDF
- pytesseract
- Pillow
- Bootstrap
- HTML/CSS

## Project Structure

```text
SmartPDF/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
└── uploads/
```

## Installation

Clone the repository:

```bash
git clone https://github.com/ibrahimt0140/smartpdf.git
cd smartpdf
```

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root directory and add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Run the application:

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000
```

## OCR Requirement

To process scanned or image-based PDFs, Tesseract OCR must be installed on your system.

Default Windows path used in the project:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

If Tesseract is installed in a different location, update the path in `app.py`.

## How It Works

1. The user uploads a PDF file.
2. The system first tries to extract text using `pdfplumber`.
3. If the PDF does not contain selectable text, the system uses OCR with `pytesseract`.
4. The extracted text is sent to Gemini AI for summarization.
5. If Gemini AI is unavailable or quota-limited, the system generates a basic local summary.
6. The summary and extracted text are displayed on the web page.

