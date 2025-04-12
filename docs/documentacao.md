# Sistema de Gestão de Inventário

Este documento fornece uma visão geral do Sistema de Gestão de Inventário, incluindo sua arquitetura, estrutura de código, funcionalidades e guias de utilização.

## Visão Geral

O Sistema de Gestão de Inventário é uma aplicação web desenvolvida em Python com Flask para processar e analisar dados de inventário extraídos de arquivos `.lst`. O sistema permite importar relatórios, visualizar inventários com filtros, editar itens, excluir registros e exportar relatórios em diversos formatos.

## Tecnologias Utilizadas

- **Python 3.8+**: Linguagem de programação base
- **Flask 2.2.3**: Framework web para desenvolvimento da aplicação
- **SQLAlchemy 3.0.3**: ORM para interação com o banco de dados
- **SQLite**: Banco de dados relacional leve
- **Pandas**: Biblioteca para manipulação e análise de dados
- **Werkzeug 2.2.3**: Utilidades para aplicações WSGI
- **Openpyxl 3.1.2**: Biblioteca para manipulação de arquivos Excel

## Estrutura do Projeto

```
Inv-Manager/
├── app/                    # Diretório principal da aplicação
│   ├── controllers/        # Controladores e rotas
│   │   └── routes.py       # Definições de rotas e lógica de controle
│   ├── models/             # Modelos de dados
│   │   └── models.py       # Definições de modelos de banco de dados
│   ├── static/             # Arquivos estáticos (CSS, JS)
│   ├── templates/          # Templates HTML
│   │   ├── base.html       # Template base com layout comum
│   │   ├── index.html      # Página inicial com lista de inventários
│   │   ├── upload.html     # Formulário de upload de arquivos
│   │   ├── view_inventario.html # Visualização detalhada de inventário
│   │   └── edit_item.html  # Formulário de edição de item
│   ├── utils/              # Utilitários
│   │   └── parser.py       # Parser para arquivos .lst
│   └── __init__.py         # Inicialização da aplicação
├── uploads/                # Diretório para armazenar arquivos importados
├── instance/               # Armazena o banco de dados SQLite
├── docs/                   # Documentação do projeto
├── requirements.txt        # Dependências do projeto
├── run.py                  # Script para execução da aplicação
└── README.md               # Informações gerais sobre o projeto
```

## Modelos de Dados

O sistema utiliza dois modelos principais para representar os dados:

### Inventario

Representa um inventário completo com múltiplos itens.

```python
class Inventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_inventario = db.Column(db.String(8), nullable=False)  # Formato: DD/MM/AA
    timestamp_extracao = db.Column(db.String(19), nullable=False)  # Formato: DD/MM/AAAA HH:MM:SS
    data_importacao = db.Column(db.DateTime, default=datetime.now)
    ultima_atualizacao = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    nome_arquivo = db.Column(db.String(255), nullable=True)
    
    itens = db.relationship('ItemInventario', backref='inventario', cascade='all, delete-orphan')
```

### ItemInventario

Representa um item específico dentro de um inventário.

```python
class ItemInventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventario_id = db.Column(db.Integer, db.ForeignKey('inventario.id'), nullable=False)
    codigo = db.Column(db.String(15), nullable=False)
    material = db.Column(db.String(100), nullable=False)
    unidade = db.Column(db.String(5), nullable=False)
    quantidade_estoque = db.Column(db.Float, nullable=False)
    quantidade_contada = db.Column(db.Float, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)
    
    # Campos para armazenar valores diretamente do arquivo
    valor_estoque_direto = db.Column(db.Float, nullable=True)
    valor_contagem_direto = db.Column(db.Float, nullable=True)
    valor_diferenca_direto = db.Column(db.Float, nullable=True)
    iv_negativo_direto = db.Column(db.Float, nullable=True)
    iv_positivo_direto = db.Column(db.Float, nullable=True)
    valor_absoluto_direto = db.Column(db.Float, nullable=True)
```

## Componentes Principais

### InventarioParser

Classe responsável por processar arquivos `.lst` e extrair dados de inventário.

```python
class InventarioParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = file_path.split('/')[-1]
        
        # Definição das posições das colunas no arquivo
        self.col_positions = {...}
    
    def processar_arquivo(self):
        # Lógica para processar o arquivo e extrair os dados
        # Retorna um objeto Inventario e lista de ItemInventario
```

### Rotas Principais

O sistema possui as seguintes rotas e funcionalidades principais:

- **/** - Lista todos os inventários
- **/upload** - Upload e processamento de novos arquivos `.lst`
- **/inventario/<id>** - Visualização detalhada de inventário com filtros
- **/inventario/<id>/edit/<item_id>** - Edição de item de inventário
- **/inventario/<id>/delete_item/<item_id>** - Exclusão de item de inventário
- **/inventario/<id>/delete** - Exclusão de inventário completo
- **/inventario/<id>/export/<format>** - Exportação de inventário em diferentes formatos

## Formato do Arquivo .lst

O sistema processa arquivos `.lst` com o seguinte formato:

```
CRISTOFOLI EQUIP BIOSSEGURANCA LTDA 
esp1107   RELATORIO DE MATERIAIS INVENTARIADOS  -  WMS                   FL.   1
                                         EXTRAIDO EM 10/04/2025 AS 15:34:28 HRS.
                                      DATA    |                    QUANTIDADE                                                     ||                         VALOR                                                                 |PRE     |
CODIGO          MATERIAL          UN. INVENT. |ESTOQUE       CONTAGEM      DIFERENCA     IV-           IV+           VAL. ABSOLUTO||ESTOQUE         CONTAGEM        DIFERENCA       IV-             IV+             VAL. ABSOLUTO  |UNIT.   |
--------------- ----------------- --- --------|------------- ------------- ------------- ------------- ------------- -------------||--------------- --------------- --------------- --------------- --------------- ---------------|--------|
MPH.01503       MOTOBOMBA AG AUT  UN  10/04/25          6,00         22,00         16,00          0,00         16,00         16,00          4172,60        15299,53        11126,93            0,00        11126,93        11126,93   695,43
 -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
TOTAL                                                   6,00         22,00         16,00          0,00         16,00         16,00          4172,60        15299,53        11126,93            0,00        11126,93        11126,93
```

### Extração da Data de Inventário

O sistema extrai a data do inventário de duas possíveis fontes:

1. **Cabeçalho do Arquivo**: A data é extraída da linha que contém "EXTRAIDO EM DD/MM/AAAA AS HH:MM:SS" e convertida para o formato DD/MM/AA.
2. **Coluna DATA INVENT.**: Se a data não for encontrada no cabeçalho, o sistema usa a data presente na coluna "DATA INVENT." do primeiro item válido.

Esse mecanismo de redundância garante que o campo obrigatório `data_inventario` seja sempre preenchido, evitando erros de restrição NOT NULL no banco de dados.

## Guia de Instalação

1. Clone o repositório:
```
git clone https://github.com/seu-usuario/inv-manager.git
cd inv-manager
```

2. Crie e ative um ambiente virtual:
```
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

3. Instale as dependências:
```
pip install -r requirements.txt
```

4. Execute a aplicação:
```
python run.py
```

5. Acesse a aplicação em seu navegador:
```
http://localhost:5000
```

## Guia de Uso

### Importar Arquivo de Inventário

1. Na página inicial, clique no botão "Importar Novo Arquivo"
2. Selecione um arquivo `.lst` válido
3. Clique em "Enviar"
4. Se o processamento for bem-sucedido, você será redirecionado para a visualização do inventário

### Visualizar Inventário

1. Na página inicial, clique em "Visualizar" ao lado do inventário desejado
2. Use os filtros disponíveis para buscar por código, material ou visualizar apenas itens com diferença
3. Os totais são exibidos no final da tabela

### Editar Item

1. Na visualização do inventário, clique no botão "Editar" ao lado do item desejado
2. Altere os valores necessários
3. Clique em "Salvar" para confirmar as alterações

### Excluir Item ou Inventário

1. Para excluir um item, clique no botão "Excluir" ao lado do item desejado
2. Para excluir um inventário completo, clique no botão "Excluir Inventário" na página de visualização do inventário

### Exportar Inventário

1. Na visualização do inventário, escolha o formato de exportação desejado:
   - Excel (.xlsx)
   - CSV (.csv)
   - TXT (.txt) - emula o formato original do arquivo `.lst`
2. O arquivo será gerado e disponibilizado para download

## Considerações Técnicas

### Validações

- **Código**: Os códigos de material devem seguir o padrão de 3 letras seguidas por ponto e 5 números (ex: MPR.01234)
- **Importação**: O sistema verifica se já existe um inventário com a mesma data e hora de extração
- **Valores**: Os campos de valores são tratados como Float para garantir precisão nos cálculos

### Tratamento de Erros na Importação

O sistema implementa as seguintes verificações durante a importação de arquivos:

1. **Validação do formato da data**: A data de inventário deve estar no formato DD/MM/AA e é extraída do cabeçalho ou da coluna DATA INVENT.
2. **Verificação de campos obrigatórios**: Todos os campos obrigatórios, incluindo a data de inventário, devem ser encontrados no arquivo.
3. **Tratamento de erros por linha**: Erros em uma linha específica não interrompem o processamento de todo o arquivo.
4. **Validação de duplicidade**: O sistema verifica se já existe um inventário com a mesma data e hora de extração.
5. **Rollback em caso de erro**: Se ocorrer um erro durante o processamento, todas as operações de banco de dados são revertidas.
6. **Tratamento robusto de valores numéricos**: O sistema implementa mecanismos de fallback para lidar com valores que não podem ser convertidos diretamente para números.
7. **Validação de linhas**: Ignora linhas que não contêm códigos de produto válidos.
8. **Tratamento de quebras de linha e espaços**: Remove caracteres problemáticos que podem interferir na conversão de valores.

As principais estratégias de tratamento de erros incluem:

- **Try-except granular**: Cada conversão de valor é tratada individualmente para evitar que um erro em um campo afete todo o processamento.
- **Extração inteligente do preço unitário**: Utiliza múltiplas estratégias para extrair esse valor que costuma apresentar desafios de posicionamento.
- **Valores calculados como fallback**: Quando não é possível extrair valores monetários diretamente do arquivo, o sistema utiliza os valores calculados com base na quantidade e preço unitário.

Quando um erro é encontrado, o sistema exibe uma mensagem detalhada ao usuário e registra informações de diagnóstico nos logs.

### Cálculos Automáticos

O sistema calcula automaticamente:

- Diferenças entre quantidades contadas e estoque
- Valores IV+ (inventário positivo) e IV- (inventário negativo)
- Valores monetários baseados nas quantidades e preços unitários
- Totais para todos os valores em cada visualização de inventário

## Futuras Melhorias

- Implementação de sistema de autenticação de usuários
- Dashboard com gráficos e indicadores de desempenho
- Integração com outros sistemas de gestão de estoque
- Adição de API para acesso programático aos dados
- Melhorias na interface do usuário para maior facilidade de uso

## Suporte

Para suporte e questões relacionadas ao sistema, entre em contato através de:

- Email: suporte@sistema-inventario.com
- Telefone: (XX) XXXX-XXXX

---

Documentação gerada em: [Data Atual]

*Versão 1.0.0* 