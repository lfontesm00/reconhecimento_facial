import cv2
import numpy as np
from datetime import datetime
import os
import logging
from model import LBPHModel
from quality_check import FaceQualityChecker
from database import FaceDatabase
from email_sender import EmailSender

class FaceRecognitionSystem:
    def __init__(self):
        """Inicializa o sistema de reconhecimento facial"""
        # Configurar sistema de logs
        self.setup_logging()
        
        self.logger.info("Iniciando sistema de reconhecimento facial")
        
        self.face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.quality_checker = FaceQualityChecker()
        self.model = LBPHModel()
        self.database = FaceDatabase()
        
        # Configurações de e-mail
        self.email_sender = EmailSender(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            email="lucasfotesm00@gmail.com",
            password="87199738Lu"
        )
        
        # Treinar modelo com dados existentes
        try:
            faces, labels = self.database.carregar_faces_treinamento()
            if faces and labels:
                self.model.train(faces, labels)
                self.logger.info(f"Modelo treinado com sucesso! ({len(faces)} faces)")
                print("Modelo treinado com sucesso!")
            else:
                self.logger.warning("Nenhuma face cadastrada para treinamento")
                print("Nenhuma face cadastrada para treinamento")
        except Exception as e:
            self.logger.error(f"Erro ao treinar modelo: {e}")
            print(f"Erro ao treinar modelo: {e}")
    
    def setup_logging(self):
        """Configura o sistema de logs"""
        # Criar diretório de logs se não existir
        os.makedirs("logs", exist_ok=True)
        
        # Configurar logger
        self.logger = logging.getLogger('FaceRecognitionSystem')
        self.logger.setLevel(logging.INFO)
        
        # Criar arquivo de log com data
        log_file = os.path.join("logs", f"execucao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        
        # Configurar formato do log
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Adicionar handler ao logger
        self.logger.addHandler(file_handler)

    def cadastrar_pessoa(self):
        """Cadastra uma nova pessoa com CPF e e-mail"""
        self.logger.info("Iniciando cadastro de nova pessoa")
        print("\n=== Cadastro de Nova Pessoa ===")
        
        # Solicitar informações
        nome = input("Nome completo: ")
        cpf = input("CPF (apenas números): ")
        email = input("E-mail: ")
        
        self.logger.info(f"Tentativa de cadastro - Nome: {nome}, CPF: {cpf}, Email: {email}")
        
        # Verificar se já existe cadastro com este CPF
        if self.database.verificar_duplicidade(cpf):
            self.logger.warning(f"Tentativa de cadastro duplicado - CPF: {cpf}")
            print("Erro: Já existe uma pessoa cadastrada com este CPF")
            return
        
        # Capturar foto
        print("\nPosicione seu rosto na área verde e mantenha a posição por 3 segundos...")
        self.logger.info("Iniciando captura de foto")
        cap = cv2.VideoCapture(0)
        
        # Definir área de guia
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        guide_size = 300
        guide_x = (frame_width - guide_size) // 2
        guide_y = (frame_height - guide_size) // 2
        
        face_capturada = None
        start_time = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Erro ao acessar a câmera")
                break
                
            # Desenhar área de guia
            cv2.rectangle(frame, (guide_x, guide_y), 
                         (guide_x + guide_size, guide_y + guide_size), 
                         (0, 255, 0), 2)
            
            # Detectar faces
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 1:
                (x, y, w, h) = faces[0]
                face_region = gray[y:y+h, x:x+w]
                
                # Verificar se a face está na área de guia
                if (guide_x <= x and x + w <= guide_x + guide_size and
                    guide_y <= y and y + h <= guide_y + guide_size):
                    
                    # Verificar qualidade
                    try:
                        quality_msg = self.quality_checker.check_quality(face_region, (x, y, w, h))
                        if quality_msg == "OK":
                            if start_time is None:
                                start_time = datetime.now()
                            else:
                                elapsed = (datetime.now() - start_time).total_seconds()
                                if elapsed >= 3:
                                    face_capturada = face_region
                                    break
                        else:
                            start_time = None
                            cv2.putText(frame, quality_msg, (10, 30),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    except Exception as e:
                        print(f"Erro na verificação de qualidade: {e}")
                        start_time = None
                else:
                    start_time = None
                    cv2.putText(frame, "Posicione o rosto na área verde", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                start_time = None
                cv2.putText(frame, "Nenhuma face detectada", (10, 30),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.imshow('Cadastro', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if face_capturada is not None:
            # Salvar face
            face_path = os.path.join(self.database.faces_dir, f"{cpf}.png")
            cv2.imwrite(face_path, face_capturada)
            
            # Cadastrar pessoa
            try:
                pessoa_id = self.database.cadastrar_pessoa(nome, cpf, email, [face_path])
                self.logger.info(f"Pessoa cadastrada com sucesso - ID: {pessoa_id}, Nome: {nome}")
                print(f"\nPessoa cadastrada com sucesso! ID: {pessoa_id}")
                
                # Enviar e-mail de confirmação
                self.email_sender.enviar_email_reconhecimento(
                    email, nome, 100.0, tipo="cadastro"
                )
                self.logger.info(f"Email de confirmação enviado para {email}")
                
                # Treinar modelo
                faces, labels = self.database.carregar_faces_treinamento()
                self.model.train(faces, labels)
                self.logger.info("Modelo retreinado com sucesso")
                print("Modelo treinado com sucesso!")
            except Exception as e:
                self.logger.error(f"Erro ao cadastrar pessoa: {e}")
                print(f"Erro ao cadastrar pessoa: {e}")
        else:
            self.logger.warning("Cadastro cancelado pelo usuário")
            print("\nCadastro cancelado")

    def monitorar(self):
        """Monitora e reconhece faces em tempo real"""
        self.logger.info("Iniciando monitoramento")
        print("\n=== Monitoramento ===")
        print("Pressione 'q' para sair")
        
        # Verificar se há faces cadastradas
        faces, labels = self.database.carregar_faces_treinamento()
        if not faces or not labels:
            self.logger.error("Tentativa de monitoramento sem faces cadastradas")
            print("Erro: Nenhuma face cadastrada para reconhecimento")
            return
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.logger.error("Não foi possível acessar a câmera")
            print("Erro: Não foi possível acessar a câmera")
            return
            
        ultimo_reconhecimento = {}  # Cache de reconhecimentos recentes
        
        while True:
            ret, frame = cap.read()
            if not ret:
                self.logger.error("Erro ao capturar frame da câmera")
                print("Erro ao capturar frame da câmera")
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                face_region = gray[y:y+h, x:x+w]
                
                # Verificar qualidade
                try:
                    quality_msg = self.quality_checker.check_quality(face_region, (x, y, w, h))
                    if quality_msg == "OK":
                        # Prever pessoa
                        pessoa_id, confianca = self.model.predict(face_region)
                        
                        if pessoa_id != -1 and confianca >= 80:
                            # Registrar reconhecimento
                            pessoa = self.database.registrar_reconhecimento(
                                pessoa_id, confianca, "monitoramento.png"
                            )
                            
                            if pessoa:
                                self.logger.info(f"Pessoa reconhecida - ID: {pessoa_id}, Nome: {pessoa['nome']}, Confiança: {confianca:.2f}%")
                                print(f"\nPessoa identificada: {pessoa['nome']}")
                                print(f"CPF: {pessoa['cpf']}")
                                print(f"E-mail: {pessoa['email']}")
                                print(f"Confiança: {confianca:.2f}%")
                                
                                # Aguardar 2 segundos e fechar
                                cv2.imshow('Monitoramento', frame)
                                cv2.waitKey(2000)
                                cap.release()
                                cv2.destroyAllWindows()
                                return
                            
                except Exception as e:
                    self.logger.error(f"Erro no processamento: {e}")
                    print(f"Erro no processamento: {e}")
            
            cv2.imshow('Monitoramento', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.logger.info("Monitoramento interrompido pelo usuário")
                break
        
        cap.release()
        cv2.destroyAllWindows()

    def gerar_relatorio(self):
        """Gera relatório de reconhecimentos"""
        self.logger.info("Iniciando geração de relatório")
        print("\n=== Gerar Relatório ===")
        data_inicio = input("Data inicial (YYYY-MM-DD): ")
        data_fim = input("Data final (YYYY-MM-DD): ")
        
        self.logger.info(f"Gerando relatório para o período: {data_inicio} a {data_fim}")
        print("\nGerando relatório...")
        
        # Simular progresso
        for i in range(101):
            barra = "=" * (i // 2) + ">" + " " * (50 - (i // 2))
            print(f"\rProgresso: [{barra}] {i}%", end="", flush=True)
            if i < 100:
                import time
                time.sleep(0.02)
        print()
        
        reconhecimentos = self.database.gerar_relatorio_periodo(data_inicio, data_fim)
        
        # Gerar nome do arquivo
        nome_arquivo = f"relatorio_{data_inicio}_a_{data_fim}.txt"
        caminho_completo = os.path.join(os.getcwd(), "relatorios", nome_arquivo)
        
        # Criar diretório de relatórios se não existir
        os.makedirs("relatorios", exist_ok=True)
        
        # Salvar relatório em arquivo
        with open(caminho_completo, "w", encoding="utf-8") as f:
            f.write("="*50 + "\n")
            f.write("RELATÓRIO DE RECONHECIMENTOS".center(50) + "\n")
            f.write("="*50 + "\n\n")
            f.write(f"Período: {data_inicio} a {data_fim}\n")
            f.write(f"Data de geração: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if reconhecimentos:
                self.logger.info(f"Encontrados {len(reconhecimentos)} reconhecimentos no período")
                f.write("Reconhecimentos encontrados:\n")
                for r in reconhecimentos:
                    f.write("\n" + "-"*30 + "\n")
                    f.write(f"Nome: {r['nome']}\n")
                    f.write(f"CPF: {r['cpf']}\n")
                    f.write(f"E-mail: {r['email']}\n")
                    f.write(f"Data/Hora: {r['data_hora']}\n")
                    f.write(f"Confiança: {r['confianca']:.2f}%\n")
            else:
                self.logger.info("Nenhum reconhecimento encontrado no período")
                f.write("\nNenhum reconhecimento encontrado no período")
        
        self.logger.info(f"Relatório gerado com sucesso: {caminho_completo}")
        print(f"\nRelatório gerado com sucesso!")
        print(f"Local do arquivo: {caminho_completo}")
        
        # Mostrar conteúdo do relatório no console
        if reconhecimentos:
            print("\nReconhecimentos encontrados:")
            for r in reconhecimentos:
                print(f"\nNome: {r['nome']}")
                print(f"CPF: {r['cpf']}")
                print(f"E-mail: {r['email']}")
                print(f"Data/Hora: {r['data_hora']}")
                print(f"Confiança: {r['confianca']:.2f}%")
        else:
            print("\nNenhum reconhecimento encontrado no período")

def main():
    system = FaceRecognitionSystem()
    
    while True:
        print("\n" + "="*50)
        print("SISTEMA DE RECONHECIMENTO FACIAL".center(50))
        print("="*50)
        print("\nOpções disponíveis:")
        print("1. Cadastrar nova pessoa")
        print("2. Iniciar monitoramento")
        print("3. Gerar relatório")
        print("4. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            system.cadastrar_pessoa()
        elif opcao == "2":
            system.monitorar()
        elif opcao == "3":
            system.gerar_relatorio()
        elif opcao == "4":
            system.logger.info("Encerrando o programa")
            print("\nEncerrando o programa...")
            break
        else:
            system.logger.warning(f"Opção inválida selecionada: {opcao}")
            print("\nOpção inválida!")

if __name__ == "__main__":
    main() 