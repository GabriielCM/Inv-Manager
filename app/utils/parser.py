import re
from datetime import datetime
from app.models.models import Inventario, ItemInventario

class InventarioParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = file_path.split('/')[-1]
        
        # Definindo as posições das colunas
        self.col_positions = {
            'codigo': (0, 15),
            'material': (16, 32),
            'unidade': (34, 36),
            'data_inventario': (38, 46),
            'estoque': (47, 62),
            'contagem': (63, 78),
            'diferenca': (79, 94),
            'iv_negativo': (95, 110),
            'iv_positivo': (111, 126),
            'val_absoluto': (127, 142),
            'valor_estoque': (144, 159),
            'valor_contagem': (160, 175),
            'valor_diferenca': (176, 191),
            'valor_iv_negativo': (192, 207),
            'valor_iv_positivo': (208, 223),
            'valor_absoluto_valor': (224, 239),
            'preco_unitario': (240, 255)
        }
    
    def processar_arquivo(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Extrair data e hora da extração
        timestamp_extracao = None
        for line in lines[:5]:  # Procurar no cabeçalho
            match = re.search(r'EXTRAIDO EM (\d{2}/\d{2}/\d{4}) AS (\d{2}:\d{2}:\d{2})', line)
            if match:
                data, hora = match.groups()
                timestamp_extracao = f"{data} {hora}"
                break
        
        if not timestamp_extracao:
            raise ValueError("Não foi possível encontrar a data e hora de extração no arquivo")
        
        # Criar objeto Inventario
        # A data do inventário será retirada do primeiro item processado
        inventario = Inventario(
            timestamp_extracao=timestamp_extracao,
            nome_arquivo=self.file_name
        )
        
        itens = []
        data_inventario_set = False
        
        # Processar linhas de itens
        for line in lines:
            # Pular linhas de cabeçalho, separadores e totais
            if (len(line.strip()) == 0 or 
                '---' in line or 
                'CODIGO' in line or 
                'CRISTOFOLI' in line or 
                'esp1107' in line or 
                'EXTRAIDO EM' in line or 
                'DATA' in line or 
                'TOTAL' in line):
                continue
            
            try:
                codigo = line[self.col_positions['codigo'][0]:self.col_positions['codigo'][1]].strip()
                material = line[self.col_positions['material'][0]:self.col_positions['material'][1]].strip()
                unidade = line[self.col_positions['unidade'][0]:self.col_positions['unidade'][1]].strip()
                data_inventario = line[self.col_positions['data_inventario'][0]:self.col_positions['data_inventario'][1]].strip()
                
                # Converter valores numéricos
                estoque_str = line[self.col_positions['estoque'][0]:self.col_positions['estoque'][1]].strip().replace(',', '.')
                contagem_str = line[self.col_positions['contagem'][0]:self.col_positions['contagem'][1]].strip().replace(',', '.')
                preco_str = line[self.col_positions['preco_unitario'][0]:self.col_positions['preco_unitario'][1]].strip().replace(',', '.')
                
                quantidade_estoque = float(estoque_str) if estoque_str else 0.0
                quantidade_contada = float(contagem_str) if contagem_str else 0.0
                preco_unitario = float(preco_str) if preco_str else 0.0
                
                # Se for o primeiro item e ainda não temos a data do inventário
                if not data_inventario_set:
                    inventario.data_inventario = data_inventario
                    data_inventario_set = True
                
                # Criar objeto ItemInventario
                item = ItemInventario(
                    codigo=codigo,
                    material=material,
                    unidade=unidade,
                    quantidade_estoque=quantidade_estoque,
                    quantidade_contada=quantidade_contada,
                    preco_unitario=preco_unitario
                )
                
                itens.append(item)
                
            except Exception as e:
                print(f"Erro ao processar linha: {line.strip()}")
                print(f"Erro: {str(e)}")
                continue
        
        return inventario, itens 