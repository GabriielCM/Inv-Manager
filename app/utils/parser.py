import re
from datetime import datetime
from app.models.models import Inventario, ItemInventario

class InventarioParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = file_path.split('/')[-1]
        
        # Definindo as posições das colunas - ajustadas para o formato correto do arquivo
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
            'preco_unitario': (240, 248)  # Ajustado para evitar sobreposição
        }
    
    def processar_arquivo(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Extrair data e hora da extração
        timestamp_extracao = None
        data_inventario = None
        for line in lines[:5]:  # Procurar no cabeçalho
            match = re.search(r'EXTRAIDO EM (\d{2}/\d{2}/\d{4}) AS (\d{2}:\d{2}:\d{2})', line)
            if match:
                data, hora = match.groups()
                timestamp_extracao = f"{data} {hora}"
                # Extrair a data de inventário do timestamp - formato DD/MM/AA
                data_inventario = data[0:6] + data[8:10]  # Converte DD/MM/AAAA para DD/MM/AA
                break
        
        if not timestamp_extracao:
            raise ValueError("Não foi possível encontrar a data e hora de extração no arquivo")
        
        # Criar objeto Inventario com a data já extraída
        inventario = Inventario(
            data_inventario=data_inventario,
            timestamp_extracao=timestamp_extracao,
            nome_arquivo=self.file_name
        )
        
        itens = []
        
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
                
                # Se a linha não começa com um código válido, pular
                if not codigo or len(codigo) < 5:
                    continue
                
                # Validar formato do código (3 letras.5 números)
                if not ItemInventario.validar_codigo(codigo):
                    print(f"Código inválido ignorado: {codigo}")
                    continue
                
                material = line[self.col_positions['material'][0]:self.col_positions['material'][1]].strip()
                unidade = line[self.col_positions['unidade'][0]:self.col_positions['unidade'][1]].strip()
                linha_data_inventario = line[self.col_positions['data_inventario'][0]:self.col_positions['data_inventario'][1]].strip()
                
                # Se não conseguimos extrair a data do cabeçalho, usar a do primeiro item
                if not data_inventario and linha_data_inventario:
                    inventario.data_inventario = linha_data_inventario
                
                # Converter valores de quantidade - tratando espaços extras e quebras de linha
                estoque_str = line[self.col_positions['estoque'][0]:self.col_positions['estoque'][1]].strip().replace(',', '.').replace('\n', '')
                contagem_str = line[self.col_positions['contagem'][0]:self.col_positions['contagem'][1]].strip().replace(',', '.').replace('\n', '')
                
                # Tratar valores monetários
                # Primeiro tentar extrair o valor, se falhar, usar um valor padrão
                try:
                    valor_estoque_str = line[self.col_positions['valor_estoque'][0]:self.col_positions['valor_estoque'][1]].strip().replace(',', '.').replace('\n', '')
                    valor_estoque = float(valor_estoque_str) if valor_estoque_str else None
                except ValueError:
                    print(f"Erro ao converter valor de estoque para {codigo}, usando valor calculado")
                    valor_estoque = None
                    
                try:
                    valor_contagem_str = line[self.col_positions['valor_contagem'][0]:self.col_positions['valor_contagem'][1]].strip().replace(',', '.').replace('\n', '')
                    valor_contagem = float(valor_contagem_str) if valor_contagem_str else None
                except ValueError:
                    print(f"Erro ao converter valor de contagem para {codigo}, usando valor calculado")
                    valor_contagem = None
                    
                try:
                    valor_diferenca_str = line[self.col_positions['valor_diferenca'][0]:self.col_positions['valor_diferenca'][1]].strip().replace(',', '.').replace('\n', '')
                    valor_diferenca = float(valor_diferenca_str) if valor_diferenca_str else None
                except ValueError:
                    print(f"Erro ao converter valor de diferença para {codigo}, usando valor calculado")
                    valor_diferenca = None
                    
                try:
                    iv_negativo_str = line[self.col_positions['iv_negativo'][0]:self.col_positions['iv_negativo'][1]].strip().replace(',', '.').replace('\n', '')
                    iv_negativo = float(iv_negativo_str) if iv_negativo_str else None
                except ValueError:
                    print(f"Erro ao converter valor de IV- para {codigo}, usando valor calculado")
                    iv_negativo = None
                    
                try:
                    iv_positivo_str = line[self.col_positions['iv_positivo'][0]:self.col_positions['iv_positivo'][1]].strip().replace(',', '.').replace('\n', '')
                    iv_positivo = float(iv_positivo_str) if iv_positivo_str else None
                except ValueError:
                    print(f"Erro ao converter valor de IV+ para {codigo}, usando valor calculado")
                    iv_positivo = None
                    
                try:
                    valor_absoluto_str = line[self.col_positions['val_absoluto'][0]:self.col_positions['val_absoluto'][1]].strip().replace(',', '.').replace('\n', '')
                    valor_absoluto = float(valor_absoluto_str) if valor_absoluto_str else None
                except ValueError:
                    print(f"Erro ao converter valor absoluto para {codigo}, usando valor calculado")
                    valor_absoluto = None
                
                # Converter quantidades
                quantidade_estoque = float(estoque_str) if estoque_str else 0.0
                quantidade_contada = float(contagem_str) if contagem_str else 0.0
                
                # Tratar preço unitário - último campo que é mais complicado de extrair
                try:
                    preco_str = line[self.col_positions['preco_unitario'][0]:].strip().split()[0].replace(',', '.').replace('\n', '')
                    preco_unitario = float(preco_str) if preco_str else 0.0
                except (ValueError, IndexError):
                    # Se não conseguir extrair o preço, tentar extrair do final da linha
                    try:
                        partes = line.strip().split()
                        preco_str = partes[-1].replace(',', '.').replace('\n', '')
                        preco_unitario = float(preco_str) if preco_str else 0.0
                    except (ValueError, IndexError):
                        print(f"Não foi possível extrair o preço unitário para {codigo}, usando 0.0")
                        preco_unitario = 0.0
                
                # Criar objeto ItemInventario
                item = ItemInventario(
                    codigo=codigo,
                    material=material,
                    unidade=unidade,
                    quantidade_estoque=quantidade_estoque,
                    quantidade_contada=quantidade_contada,
                    preco_unitario=preco_unitario,
                    # Adicionar valores monetários diretos
                    valor_estoque_direto=valor_estoque,
                    valor_contagem_direto=valor_contagem,
                    valor_diferenca_direto=valor_diferenca,
                    iv_negativo_direto=iv_negativo,
                    iv_positivo_direto=iv_positivo,
                    valor_absoluto_direto=valor_absoluto
                )
                
                itens.append(item)
                print(f"Item processado com sucesso: {codigo}")
                
            except Exception as e:
                print(f"Erro ao processar linha: {line.strip()}")
                print(f"Erro: {str(e)}")
                continue
                
        # Verificação final: se ainda não temos data_inventario, levantar erro
        if not inventario.data_inventario:
            raise ValueError("Não foi possível extrair a data do inventário do arquivo")
        
        print(f"Total de itens processados: {len(itens)}")
        return inventario, itens 