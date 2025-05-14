# Arquitetura do Sistema de Reconhecimento Facial

## 1. Visão Geral da Arquitetura

O sistema é composto por três módulos principais:

1. **Captura e Pré-processamento**
2. **Reconhecimento Facial**
3. **Armazenamento e Gerenciamento de Dados**

## 2. Componentes Principais

### 2.1 Captura e Pré-processamento (`main.py`)

```python
class FaceRecognitionSystem:
    def __init__(self):
        self.face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.quality_checker = FaceQualityChecker()
        self.model = LBPHModel()
        self.database = FaceDatabase()
```

#### Funcionalidades:

- **Detecção de Faces**: Utiliza o classificador Haar Cascade para detectar rostos
- **Controle de Qualidade**: Implementa verificações de iluminação, contraste e posicionamento
- **Interface de Usuário**: Fornece feedback visual e instruções em tempo real

### 2.2 Modelo de Reconhecimento (`model.py`)

```python
class LBPHModel:
    def __init__(self):
        self.model = cv2.face.LBPHFaceRecognizer_create(
            radius=1,
            neighbors=8,
            grid_x=8,
            grid_y=8,
            threshold=100
        )
```

#### Características:

- **Algoritmo**: LBPH (Local Binary Patterns Histograms)
- **Parâmetros**:
  - `radius`: 1 (captura detalhes locais)
  - `neighbors`: 8 (tolerância a variações)
  - `grid_x/grid_y`: 8x8 (resolução do reconhecimento)
  - `threshold`: 100 (limiar de confiança)

### 2.3 Verificação de Qualidade (`quality_check.py`)

```python
class FaceQualityChecker:
    def __init__(self):
        self.min_brightness = 20
        self.max_brightness = 230
        self.min_contrast = 15
        self.min_face_size = 100
        self.max_face_size = 400
        self.max_angle = 30
```

#### Critérios de Qualidade:

- **Brilho**: 20-230 (tolerância a variações de iluminação)
- **Contraste**: Mínimo de 15
- **Tamanho da Face**: 100-400 pixels
- **Ângulo**: Máximo de 30 graus

### 2.4 Armazenamento de Dados (`database.py`)

```python
class FaceDatabase:
    def __init__(self):
        self.pessoas_file = 'pessoas.json'
        self.reconhecimentos_file = 'reconhecimentos.json'
        self.faces_dir = 'faces_db/faces'
```

#### Funcionalidades:

- **Armazenamento de Faces**: Salva imagens em formato PNG
- **Gerenciamento de Pessoas**: Mantém registro de usuários cadastrados
- **Registro de Reconhecimentos**: Armazena histórico de acessos

## 3. Fluxo de Processamento

### 3.1 Cadastro de Usuários

1. Captura da imagem
2. Verificação de qualidade
3. Extração de características faciais
4. Armazenamento no banco de dados

### 3.2 Reconhecimento

1. Detecção de faces
2. Verificação de qualidade
3. Extração de características
4. Comparação com banco de dados
5. Cálculo de confiança

### 3.3 Monitoramento

1. Captura contínua de frames
2. Detecção e reconhecimento em tempo real
3. Registro de acessos
4. Feedback visual

## 4. Bibliotecas Utilizadas

- **OpenCV**: Processamento de imagens e reconhecimento facial
- **NumPy**: Manipulação de arrays e cálculos matemáticos
- **JSON**: Armazenamento de dados estruturados
- **OS**: Gerenciamento de arquivos e diretórios

## 5. Considerações Técnicas

### 5.1 Performance

- Processamento em tempo real
- Otimização para webcam
- Balanceamento entre precisão e velocidade

### 5.2 Segurança

- Armazenamento local de dados
- Validação de qualidade
- Proteção contra falsos positivos

### 5.3 Escalabilidade

- Estrutura modular
- Facilidade de manutenção
- Possibilidade de expansão

## 6. Limitações Técnicas

1. **Hardware**:

   - Dependência de câmera de qualidade
   - Requisitos de processamento

2. **Ambiente**:

   - Sensibilidade à iluminação
   - Necessidade de posicionamento adequado

3. **Software**:
   - Limitações do algoritmo LBPH
   - Trade-off entre precisão e velocidade
