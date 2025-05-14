# Sistema de Reconhecimento Facial

Sistema de reconhecimento facial com cadastro único por CPF e notificação por e-mail.

## Funcionalidades

- Cadastro de pessoas com CPF único
- Verificação de qualidade facial
- Reconhecimento em tempo real
- Notificação por e-mail
- Geração de relatórios

## Requisitos

- Python 3.8+
- OpenCV
- NumPy
- SMTP para envio de e-mails

## Instalação

1. Clone o repositório
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Configuração

1. Configure as credenciais de e-mail no arquivo `main.py`:

```python
self.email_sender = EmailSender(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    email="seu_email@gmail.com",
    password="sua_senha"
)
```

## Uso

1. Execute o programa:

```bash
python main.py
```

2. Escolha uma opção no menu:
   - 1: Cadastrar nova pessoa
   - 2: Iniciar monitoramento
   - 3: Gerar relatório
   - 4: Sair

### Cadastro

- Informe nome completo, CPF e e-mail
- Posicione o rosto na área verde
- Mantenha a posição por 3 segundos
- O sistema validará a qualidade da imagem

### Monitoramento

- O sistema detectará faces automaticamente
- Pessoas reconhecidas terão retângulo verde
- Não reconhecidas terão retângulo vermelho
- E-mails serão enviados para pessoas reconhecidas

### Relatórios

- Selecione o período desejado
- Visualize os reconhecimentos realizados
- Dados incluídos: nome, CPF, e-mail, data/hora e confiança

## Estrutura de Arquivos

- `main.py`: Interface principal do sistema
- `database.py`: Gerenciamento de dados
- `model.py`: Modelo de reconhecimento facial
- `quality_check.py`: Verificação de qualidade
- `email_sender.py`: Envio de notificações
- `faces/`: Diretório de imagens faciais
- `pessoas.json`: Registro de pessoas cadastradas
- `reconhecimentos.json`: Histórico de reconhecimentos

## Segurança

- CPFs são únicos no sistema
- E-mails são enviados apenas para pessoas reconhecidas
- Dados são armazenados localmente em formato JSON

## Limitações

- Requer boa iluminação
- Necessita de rosto visível e estável
- Depende da qualidade da câmera
- Requer conexão com internet para envio de e-mails
"# reconhecimento_facial" 
