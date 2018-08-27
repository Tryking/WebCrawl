try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract

print('start')
print(pytesseract.image_to_string(Image.open('12.png')))
print('end')
