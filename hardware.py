class Webcam:
    def __init__(self, camera_index=0):
        import cv2
        self.cv2 = cv2
        self.camera_index = camera_index
        self.cap = None

    def start(self):
        self.cap = self.cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Não foi possível abrir a webcam no índice {self.camera_index}")

    def read_frame(self):
        if self.cap is None:
            raise RuntimeError("Webcam não iniciada. Chame start() antes.")
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Não foi possível capturar frame da webcam.")
        return frame

    def release(self):
        if self.cap:
            self.cap.release() 