import csv
import cv2
import datetime

def log_metrics(metrics, csv_path="metrics_log.csv"):
    """
    Salva métricas em um arquivo CSV.
    metrics: dicionário com métricas.
    """
    fieldnames = list(metrics.keys())
    try:
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(metrics)
    except Exception as e:
        print(f"Erro ao salvar métricas: {e}")

def save_screenshot(image, path=None):
    """
    Salva uma imagem (frame) em disco. Se path não for fornecido, usa timestamp.
    """
    if path is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"screenshot_{timestamp}.png"
    try:
        cv2.imwrite(path, image)
    except Exception as e:
        print(f"Erro ao salvar screenshot: {e}") 