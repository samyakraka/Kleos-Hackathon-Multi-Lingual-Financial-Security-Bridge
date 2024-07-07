import pytesseract
from PIL import Image

# Set the path to the Tesseract executable
# Update the path below according to your Tesseract installation path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Now you can use pytesseract as usual
img = Image.open('quote.png')
text = pytesseract.image_to_string(img)
print(text)