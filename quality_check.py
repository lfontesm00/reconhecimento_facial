import cv2
import numpy as np

class FaceQualityChecker:
    def __init__(self):
        # Parâmetros de qualidade
        self.min_brightness = 20
        self.max_brightness = 230
        self.min_contrast = 15
        self.min_face_size = 100
        self.max_face_size = 400
        self.max_angle = 30

    def check_quality(self, face_image, face_coords):
        """Verifica a qualidade da imagem facial"""
        try:
            x, y, w, h = face_coords
            
            # Verificar tamanho
            if w < self.min_face_size:
                return "Aproxime-se da câmera"
            if w > self.max_face_size:
                return "Afaste-se da câmera"
            
            # Verificar brilho
            brightness = np.mean(face_image)
            if brightness < self.min_brightness:
                return "Ambiente muito escuro"
            if brightness > self.max_brightness:
                return "Ambiente muito claro"
            
            # Verificar contraste
            contrast = np.std(face_image)
            if contrast < self.min_contrast:
                return "Baixo contraste"
            
            # Verificar ângulo
            # Simplificado: usa proporção largura/altura
            aspect_ratio = w / h
            if abs(1 - aspect_ratio) > (self.max_angle / 100):
                return "Mantenha o rosto reto"
            
            return "OK"
            
        except Exception as e:
            print(f"Erro na verificação de qualidade: {e}")
            return "Erro na verificação"
    
    def _estimate_face_angle(self, face_img):
        """Estima o ângulo de inclinação do rosto"""
        # Detecta bordas
        edges = cv2.Canny(face_img, 50, 150)
        
        # Encontra linhas
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=50)
        
        if lines is None:
            return 0
        
        # Calcula ângulo médio das linhas
        angles = []
        for rho, theta in lines[:, 0]:
            angle = np.degrees(theta) - 90
            if -45 <= angle <= 45:  # Considera apenas linhas aproximadamente horizontais
                angles.append(angle)
        
        if not angles:
            return 0
        
        return np.mean(angles)
    
    def enhance_quality(self, face_img):
        """Melhora a qualidade da imagem"""
        # Aplica equalização adaptativa
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(face_img)
        
        # Aplica suavização leve
        enhanced = cv2.GaussianBlur(enhanced, (3,3), 0)
        
        return enhanced 