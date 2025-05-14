import os
import json
from datetime import datetime
import cv2
import numpy as np

class FaceDatabase:
    def __init__(self):
        """Inicializa o banco de dados"""
        self.pessoas_file = "pessoas.json"
        self.reconhecimentos_file = "reconhecimentos.json"
        self.faces_dir = "faces"
        
        # Criar diretórios se não existirem
        os.makedirs(self.faces_dir, exist_ok=True)
        
        # Inicializar arquivos se não existirem
        if not os.path.exists(self.pessoas_file):
            with open(self.pessoas_file, 'w') as f:
                json.dump([], f)
                
        if not os.path.exists(self.reconhecimentos_file):
            with open(self.reconhecimentos_file, 'w') as f:
                json.dump([], f)
                
        # Migrar dados antigos se necessário
        self.migrar_dados_antigos()
    
    def migrar_dados_antigos(self):
        """Migra dados do formato antigo para o novo formato"""
        try:
            with open(self.pessoas_file, 'r') as f:
                pessoas = json.load(f)
                
            if pessoas and 'cpf' not in pessoas[0]:
                print("Migrando dados antigos para o novo formato...")
                novas_pessoas = []
                
                for pessoa in pessoas:
                    nova_pessoa = {
                        'id': pessoa['id'],
                        'nome': pessoa['nome'],
                        'cpf': str(pessoa['id']),  # Usa o ID como CPF temporário
                        'email': f"{pessoa['nome'].lower().replace(' ', '.')}@exemplo.com",
                        'face_paths': pessoa['faces'],
                        'data_cadastro': pessoa['data_cadastro']
                    }
                    novas_pessoas.append(nova_pessoa)
                
                with open(self.pessoas_file, 'w') as f:
                    json.dump(novas_pessoas, f, indent=4)
                    
                print("Migração concluída com sucesso!")
                
        except Exception as e:
            print(f"Erro na migração dos dados: {e}")

    def verificar_duplicidade(self, cpf):
        """Verifica se já existe uma pessoa cadastrada com o CPF informado"""
        with open(self.pessoas_file, 'r') as f:
            pessoas = json.load(f)
            
        for pessoa in pessoas:
            if pessoa['cpf'] == cpf:
                return True
                
        return False

    def cadastrar_pessoa(self, nome, cpf, email, face_paths):
        """Cadastra uma nova pessoa com CPF e e-mail"""
        with open(self.pessoas_file, 'r') as f:
            pessoas = json.load(f)
            
        # Gerar novo ID
        if pessoas:
            novo_id = max(p['id'] for p in pessoas) + 1
        else:
            novo_id = 1
            
        nova_pessoa = {
            'id': novo_id,
            'nome': nome,
            'cpf': cpf,
            'email': email,
            'face_paths': face_paths,
            'data_cadastro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        pessoas.append(nova_pessoa)
        
        with open(self.pessoas_file, 'w') as f:
            json.dump(pessoas, f, indent=4)
            
        return novo_id
    
    def carregar_faces_treinamento(self):
        """Carrega faces para treinamento do modelo"""
        with open(self.pessoas_file, 'r') as f:
            pessoas = json.load(f)
            
        faces = []
        labels = []
        
        for pessoa in pessoas:
            for face_path in pessoa['face_paths']:
                if os.path.exists(face_path):
                    face = cv2.imread(face_path, cv2.IMREAD_GRAYSCALE)
                    if face is not None:
                        faces.append(face)
                        labels.append(pessoa['id'])
                        
        return faces, labels
    
    def get_pessoa_info(self, pessoa_id):
        """Retorna informações da pessoa pelo ID"""
        with open(self.pessoas_file, 'r') as f:
            pessoas = json.load(f)
            for pessoa in pessoas:
                if pessoa['id'] == pessoa_id:
                    return pessoa
        return None
    
    def registrar_reconhecimento(self, pessoa_id, confianca, face_path):
        """Registra um reconhecimento e retorna os dados da pessoa"""
        with open(self.pessoas_file, 'r') as f:
            pessoas = json.load(f)
            
        pessoa = next((p for p in pessoas if p['id'] == pessoa_id), None)
        if not pessoa:
            return None
            
        with open(self.reconhecimentos_file, 'r') as f:
            reconhecimentos = json.load(f)
            
        novo_reconhecimento = {
            'pessoa_id': pessoa_id,
            'nome': pessoa['nome'],
            'cpf': pessoa['cpf'],
            'email': pessoa['email'],
            'confianca': confianca,
            'face_path': face_path,
            'data_hora': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        reconhecimentos.append(novo_reconhecimento)
        
        with open(self.reconhecimentos_file, 'w') as f:
            json.dump(reconhecimentos, f, indent=4)
            
        return pessoa
    
    def gerar_relatorio_periodo(self, data_inicio, data_fim):
        """Gera relatório de reconhecimentos no período especificado"""
        with open(self.reconhecimentos_file, 'r') as f:
            reconhecimentos = json.load(f)
            
        data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
        data_fim = datetime.strptime(data_fim, "%Y-%m-%d")
        
        reconhecimentos_periodo = []
        for r in reconhecimentos:
            data_hora = datetime.strptime(r['data_hora'], "%Y-%m-%d %H:%M:%S")
            if data_inicio <= data_hora <= data_fim:
                reconhecimentos_periodo.append(r)
                
        return reconhecimentos_periodo 