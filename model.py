import cv2
import numpy as np

class LBPHModel:
    def __init__(self):
        # Ajustando parâmetros para melhor precisão
        self.radius = 1  # Reduzido para capturar mais detalhes locais
        self.neighbors = 8  # Reduzido para ser mais tolerante
        self.grid_x = 8  # Mantido para boa resolução
        self.grid_y = 8  # Mantido para boa resolução
        self.threshold = 100  # Aumentado para ser mais tolerante
        self.model = cv2.face.LBPHFaceRecognizer_create(
            radius=self.radius,
            neighbors=self.neighbors,
            grid_x=self.grid_x,
            grid_y=self.grid_y,
            threshold=self.threshold
        )
        self.last_predictions = {}  # Cache de predições recentes
    
    def train(self, faces, labels):
        """Treina o modelo com as faces fornecidas"""
        if not faces or not labels:
            raise ValueError("Listas de faces e labels não podem estar vazias")
        
        print(f"Treinando modelo com {len(faces)} faces...")  # Log de debug
        
        # Aplica pré-processamento em todas as faces
        processed_faces = []
        for face in faces:
            # Aplica equalização adaptativa
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(face)
            
            # Aplica suavização leve
            enhanced = cv2.GaussianBlur(enhanced, (3,3), 0)
            
            processed_faces.append(enhanced)
        
        self.model.train(processed_faces, np.array(labels))
        self.last_predictions.clear()  # Limpa cache ao treinar
        print("Modelo treinado com sucesso!")  # Log de debug
    
    def predict(self, face_img):
        """Faz a predição para uma face"""
        try:
            # Aplica o mesmo pré-processamento do treino
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(face_img)
            enhanced = cv2.GaussianBlur(enhanced, (3,3), 0)
            
            # Verifica cache
            face_hash = hash(enhanced.tobytes())
            if face_hash in self.last_predictions:
                return self.last_predictions[face_hash]
            
            # Faz predição
            label, confidence = self.model.predict(enhanced)
            
            # Ajusta a confiança para ser mais intuitiva
            # Quanto menor o valor, melhor a confiança
            adjusted_confidence = min(100, max(0, confidence))
            
            print(f"Predição: ID={label}, Confiança={adjusted_confidence:.2f}")  # Log de debug
            
            # Armazena no cache
            self.last_predictions[face_hash] = (label, adjusted_confidence)
            
            # Limita tamanho do cache
            if len(self.last_predictions) > 100:
                self.last_predictions.pop(next(iter(self.last_predictions)))
            
            return label, adjusted_confidence
            
        except Exception as e:
            print(f"Erro na predição: {e}")  # Log de erro
            return -1, 100  # Retorna desconhecido em caso de erro 