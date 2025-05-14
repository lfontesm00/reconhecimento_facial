import cv2
import numpy as np

class FaceDetector:
    def __init__(self):
        # Carrega o classificador Haar Cascade para detecção facial
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.last_frame = None
        self.last_faces = []
    
    def detect_faces(self, frame):
        """
        Detecta faces em um frame e retorna uma lista de regiões (x, y, w, h)
        """
        # Reduz o tamanho do frame para melhor performance
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        
        # Otimizações para detecção mais rápida
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=3,  # Reduzido para detecção mais rápida
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # Ajusta as coordenadas para o tamanho original
        faces = [(x*2, y*2, w*2, h*2) for (x, y, w, h) in faces]
        
        # Filtra faces muito próximas
        faces = self._filter_overlapping_faces(faces)
        
        self.last_frame = frame
        self.last_faces = faces
        return faces
    
    def _filter_overlapping_faces(self, faces):
        """Remove detecções redundantes de faces"""
        if len(faces) <= 1:
            return faces
            
        filtered = []
        for i, (x1, y1, w1, h1) in enumerate(faces):
            keep = True
            for j, (x2, y2, w2, h2) in enumerate(faces):
                if i != j:
                    # Calcula a interseção
                    x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
                    y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
                    overlap_area = x_overlap * y_overlap
                    
                    # Se a interseção for maior que 50% da área menor, remove uma
                    if overlap_area > 0.5 * min(w1*h1, w2*h2):
                        if w1*h1 < w2*h2:
                            keep = False
                            break
            
            if keep:
                filtered.append((x1, y1, w1, h1))
        
        return filtered
    
    def extract_face(self, frame, face_region, size=(100, 100)):
        """
        Extrai e pré-processa uma face de um frame
        """
        x, y, w, h = face_region
        
        # Aumenta a região da face para incluir mais contexto
        padding = int(min(w, h) * 0.2)
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(frame.shape[1] - x, w + 2*padding)
        h = min(frame.shape[0] - y, h + 2*padding)
        
        face = frame[y:y+h, x:x+w]
        face_gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        face_resized = cv2.resize(face_gray, size)
        
        # Aplica equalização adaptativa para melhor contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        face_equalized = clahe.apply(face_resized)
        
        return face_equalized
    
    def draw_face_rectangle(self, frame, face_region, nome=None, confianca=None, cor=(0, 255, 0)):
        """Desenha retângulo ao redor da face detectada"""
        x, y, w, h = face_region
        
        # Desenha retângulo
        cv2.rectangle(frame, (x, y), (x+w, y+h), cor, 2)
        
        # Adiciona nome e confiança se fornecidos
        if nome is not None:
            texto = f"{nome}"
            if confianca is not None:
                texto += f" ({confianca:.1f})"
            
            # Calcula posição do texto
            (text_w, text_h), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            
            # Desenha fundo para o texto
            cv2.rectangle(frame, (x, y - text_h - 10), (x + text_w, y), cor, -1)
            
            # Desenha texto
            cv2.putText(frame, texto, (x, y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2) 