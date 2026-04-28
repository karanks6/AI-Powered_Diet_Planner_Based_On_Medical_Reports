
import os
TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
POPPLER_PATH = os.getenv("POPPLER_PATH", r"C:\Program Files\poppler-0.68.0\bin")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "output")
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf","png","jpg","jpeg","tiff"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
