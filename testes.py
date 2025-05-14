import os
import time
from datetime import datetime
from hardware import Webcam
from processing import to_grayscale, resize, equalize
from model import LBPHModel
from evaluation import run_tests
from logger import log_metrics, save_screenshot
import cv2

def testar_webcam():
    """Testa a captura de frames da webcam"""
    print("\n=== Testando Webcam ===")
    try:
        webcam = Webcam()
        webcam.start()
        print("Webcam iniciada com sucesso")
        
        # Captura 3 frames com um pequeno intervalo
        for i in range(3):
            frame = webcam.read_frame()
            print(f"Frame {i+1} capturado com sucesso")
            
            # Verificar o brilho da imagem
            media_pixels = cv2.mean(frame)[0]
            print(f"Brilho médio do frame {i+1}: {media_pixels:.2f}")
            
            if media_pixels < 10:  # Se a média for menor que 10, provavelmente está fechada
                print("AVISO: A câmera parece estar fechada ou bloqueada!")
                print("Por favor, verifique se a câmera está desbloqueada e tente novamente.")
            elif media_pixels > 200:  # Se a média for maior que 200, está muito clara
                print("AVISO: A imagem está muito clara!")
                print("Por favor, verifique se há muita luz direta na câmera.")
            
            # Ajustar brilho e contraste baseado no brilho médio
            if media_pixels > 200:
                alpha = 0.8  # Reduzir contraste
                beta = -30   # Reduzir brilho
            elif media_pixels < 50:
                alpha = 1.5  # Aumentar contraste
                beta = 50    # Aumentar brilho
            else:
                alpha = 1.2  # Contraste normal
                beta = 10    # Brilho normal
                
            frame_ajustado = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
            save_screenshot(frame_ajustado, f"teste_webcam_{i+1}.png")
            time.sleep(0.5)  # Pequeno intervalo entre capturas
        
        webcam.release()
        return True
    except Exception as e:
        print(f"Erro ao testar webcam: {e}")
        return False

def testar_preprocessamento():
    """Testa as funções de pré-processamento"""
    print("\n=== Testando Pré-processamento ===")
    try:
        # Capturar uma imagem real da webcam
        webcam = Webcam()
        webcam.start()
        frame = webcam.read_frame()
        webcam.release()
        
        # Testar conversão para escala de cinza
        cinza = to_grayscale(frame)
        print("Conversão para escala de cinza: OK")
        save_screenshot(cinza, "teste_cinza.png")
        
        # Testar redimensionamento
        redim = resize(cinza, (200, 200))  # Aumentando o tamanho para melhor visualização
        print("Redimensionamento: OK")
        save_screenshot(redim, "teste_redim.png")
        
        # Testar equalização
        equal = equalize(cinza)
        print("Equalização: OK")
        save_screenshot(equal, "teste_equal.png")
        
        return True
    except Exception as e:
        print(f"Erro ao testar pré-processamento: {e}")
        return False

def testar_modelo():
    """Testa o treinamento e predição do modelo LBPH"""
    print("\n=== Testando Modelo LBPH ===")
    try:
        # Criar imagens de teste
        import numpy as np
        img1 = np.zeros((100, 100), dtype=np.uint8)
        img2 = np.ones((100, 100), dtype=np.uint8) * 255
        
        # Treinar modelo
        model = LBPHModel()
        model.train([img1, img2], [0, 1])
        print("Treinamento do modelo: OK")
        
        # Testar predição
        label, conf = model.predict(img1)
        print(f"Predição: label={label}, confiança={conf}")
        
        return True
    except Exception as e:
        print(f"Erro ao testar modelo: {e}")
        return False

def testar_avaliacao():
    """Testa a avaliação de métricas"""
    print("\n=== Testando Avaliação ===")
    try:
        # Criar cenário de teste
        import numpy as np
        img = np.zeros((100, 100), dtype=np.uint8)
        scenarios = [{
            'images': [img, img],
            'labels': [0, 0],
            'nome': 'teste_avaliacao'
        }]
        
        # Criar modelo de teste
        model = LBPHModel()
        model.train([img], [0])
        
        # Executar testes
        resultados = run_tests(scenarios, model, lambda x: x)
        print("Avaliação concluída com sucesso")
        print(f"Resultados salvos em: resultados.csv")
        
        return True
    except Exception as e:
        print(f"Erro ao testar avaliação: {e}")
        return False

def gerar_relatorio(resultados):
    """Gera um relatório detalhado dos testes"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    relatorio_path = f"relatorio_testes_{timestamp}.txt"
    
    with open(relatorio_path, 'w', encoding='utf-8') as f:
        f.write("=== Relatório de Testes ===\n")
        f.write(f"Data e Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        
        for teste, sucesso in resultados.items():
            status = "SUCESSO" if sucesso else "FALHA"
            f.write(f"{teste}: {status}\n")
        
        f.write("\nObservações:\n")
        f.write("- Verifique os arquivos de screenshot gerados\n")
        f.write("- Verifique o arquivo resultados.csv para métricas\n")
        f.write("- Verifique o arquivo metrics_log.csv para logs\n")
    
    print(f"\nRelatório gerado em: {relatorio_path}")

def main():
    """Função principal que executa todos os testes"""
    print("Iniciando testes...")
    
    resultados = {
        "Webcam": testar_webcam(),
        "Pré-processamento": testar_preprocessamento(),
        "Modelo LBPH": testar_modelo(),
        "Avaliação": testar_avaliacao()
    }
    
    # Log das métricas gerais
    log_metrics({
        'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'webcam': int(resultados["Webcam"]),
        'preprocessamento': int(resultados["Pré-processamento"]),
        'modelo': int(resultados["Modelo LBPH"]),
        'avaliacao': int(resultados["Avaliação"])
    })
    
    gerar_relatorio(resultados)
    print("\nTestes concluídos!")

if __name__ == "__main__":
    main() 