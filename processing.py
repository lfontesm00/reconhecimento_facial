import cv2

def to_grayscale(image):
    """Converte uma imagem para escala de cinza."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def resize(image, size):
    """Redimensiona a imagem para o tamanho especificado (width, height)."""
    return cv2.resize(image, size)

def equalize(image):
    """Equaliza o histograma da imagem em escala de cinza."""
    return cv2.equalizeHist(image) 