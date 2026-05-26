from flask import Flask, render_template, request
import os
import io
import pdfplumber
import pytesseract
import fitz  # PyMuPDF
from PIL import Image
from dotenv import load_dotenv
from google import genai

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load environment variables from the .env file
load_dotenv()

# Get Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Tesseract OCR executable path
# Update this path if Tesseract is installed in a different location
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_written_pdf(pdf_path):
    """
    Extracts text from text-based PDF files.
    Example: PDFs exported from Word or other document editors.
    """
    text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

    except Exception as e:
        print("Text-based PDF extraction error:", e)

    return text


def extract_text_from_image_pdf(pdf_path):
    """
    Extracts text from scanned or image-based PDF files using OCR.
    PyMuPDF converts each PDF page into an image.
    Tesseract OCR reads the text from each image.
    """
    text = ""

    try:
        pdf_document = fitz.open(pdf_path)

        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]

            # Convert the PDF page into a high-resolution image
            pix = page.get_pixmap(dpi=300)

            # Convert image data to PNG format
            img_data = pix.tobytes("png")

            # Create a PIL image object
            image = Image.open(io.BytesIO(img_data))

            # Extract text from the image using OCR
            page_text = pytesseract.image_to_string(image)

            if page_text:
                text += page_text + "\n"

        pdf_document.close()

    except Exception as e:
        print("OCR extraction error:", e)
        raise e

    return text


def extract_text_from_pdf(pdf_path):
    """
    Tries to extract text from the PDF using normal text extraction first.
    If not enough text is found, it uses OCR for scanned PDFs.
    """
    text = extract_text_from_written_pdf(pdf_path)

    # If enough text is extracted, OCR is not needed
    if len(text.strip()) >= 50:
        return text

    # If no readable text is found, use OCR
    text = extract_text_from_image_pdf(pdf_path)

    return text


def simple_local_summary(text, sentence_count=5):
    """
    Creates a simple local summary when Gemini AI is unavailable.
    It selects the first meaningful sentences from the extracted text.
    """
    text = text.replace("\n", " ")
    sentences = text.split(".")

    clean_sentences = []

    for sentence in sentences:
        sentence = sentence.strip()

        if len(sentence) > 40:
            clean_sentences.append(sentence)

    summary = ". ".join(clean_sentences[:sentence_count])

    if summary:
        summary += "."

    return summary


def summarize_with_gemini(text):
    """
    Generates a summary using Gemini AI.
    If Gemini is unavailable, quota-limited, or returns an error,
    the application falls back to local summarization.
    """
    if not GEMINI_API_KEY:
        return simple_local_summary(text)

    max_chars = 6000
    text_for_ai = text[:max_chars]

    prompt = f"""
Summarize the following PDF content.

Rules:
- Write in the same language as the PDF.
- Use simple and clear language.
- Give 5 bullet points.
- Do not add information that is not in the PDF.

PDF content:
{text_for_ai}
"""

    models = [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash"
    ]

    for model_name in models:
        try:
            response = gemini_client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            return response.text

        except Exception as e:
            print(f"Gemini error with {model_name}: {type(e).__name__} - {str(e)}")

    local_summary = simple_local_summary(text)

    return f"""
Gemini AI is currently unavailable or quota-limited.

Local Summary:
{local_summary}
"""


@app.route("/", methods=["GET", "POST"])
def index():
    summary = None
    filename = None
    extracted_text = None
    error = None

    if request.method == "POST":
        file = request.files.get("pdf_file")

        if not file:
            error = "Please upload a PDF file."

        elif not file.filename.lower().endswith(".pdf"):
            error = "Only PDF files are allowed."

        else:
            filename = file.filename
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            file.save(file_path)

            try:
                extracted_text = extract_text_from_pdf(file_path)

                if extracted_text and extracted_text.strip():
                    summary = summarize_with_gemini(extracted_text)
                else:
                    error = "No readable text found in this PDF."

            except Exception as e:
                error = f"PDF/OCR error: {type(e).__name__} - {str(e)}"

    return render_template(
        "index.html",
        summary=summary,
        filename=filename,
        extracted_text=extracted_text,
        error=error
    )


if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.run(debug=True)