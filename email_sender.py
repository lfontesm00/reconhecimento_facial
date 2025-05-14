import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailSender:
    def __init__(self, smtp_server, smtp_port, email, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email
        self.password = password

    def enviar_email_reconhecimento(self, destinatario, nome, confianca, tipo="cadastro"):
        """Envia e-mail de notificação"""
        try:
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = destinatario
            
            if tipo == "cadastro":
                msg['Subject'] = "Cadastro no Sistema de Reconhecimento Facial"
                corpo = f"""
                Olá {nome},

                Seu cadastro no sistema de reconhecimento facial foi realizado com sucesso!

                Detalhes do cadastro:
                - Data/Hora: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
                - Status: Cadastro concluído

                Este é um e-mail automático, por favor não responda.
                """
            else:
                msg['Subject'] = "Reconhecimento Facial - Sistema de Monitoramento"
                corpo = f"""
                Olá {nome},

                Você foi reconhecido pelo sistema de monitoramento facial.

                Detalhes do reconhecimento:
                - Data/Hora: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
                - Nível de confiança: {confianca:.2f}%

                Este é um e-mail automático, por favor não responda.
                """
            
            msg.attach(MIMEText(corpo, 'plain'))

            # Enviar e-mail
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()  # Identifica-se com o servidor
                server.starttls()  # Inicia conexão segura
                server.ehlo()  # Identifica-se novamente após TLS
                server.login(self.email, self.password)
                server.send_message(msg)
                
            print(f"E-mail enviado com sucesso para {destinatario}")
            return True
            
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")
            return False 