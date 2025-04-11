# Sistema de Gestão de Inventário

Sistema para gerenciamento de inventário diário que processa dados extraídos de arquivos .lst. Desenvolvido em Python com Flask e SQLite.

## Funcionalidades

- Importação e processamento de arquivos .lst com relatórios de inventário
- Visualização detalhada de inventários com filtros por código, material ou apenas itens com diferença
- Edição de itens do inventário, permitindo atualizar a quantidade contada
- Exclusão de inventários completos ou itens específicos
- Exportação de relatórios em diversos formatos (Excel, CSV, TXT)

## Requisitos

- Python 3.8+
- Flask 2.2.3
- Flask-SQLAlchemy 3.0.3
- Pandas 1.5.3
- Werkzeug 2.2.3
- Openpyxl 3.1.2

## Instalação

1. Clone o repositório:
```
git clone https://github.com/seu-usuario/inv-manager.git
cd inv-manager
```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):
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

## Uso

1. Execute a aplicação:
```
python run.py
```

2. Acesse a aplicação em seu navegador: `http://localhost:5000`

3. Faça upload de arquivos .lst através da interface da aplicação

## Estrutura do Projeto

```
Inv-Manager/
├── app/                    # Diretório principal da aplicação
│   ├── controllers/        # Controladores e rotas
│   ├── models/             # Modelos de dados
│   ├── static/             # Arquivos estáticos (CSS, JS)
│   ├── templates/          # Templates HTML
│   ├── utils/              # Utilitários (parser, etc.)
│   └── __init__.py         # Inicialização da aplicação
├── uploads/                # Diretório para armazenar arquivos importados
├── requirements.txt        # Dependências do projeto
├── run.py                  # Script para execução da aplicação
└── README.md               # Este arquivo
```

## Formato de Arquivo .lst

O sistema espera arquivos no seguinte formato:

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

## Licença

Este projeto está licenciado sob a licença MIT.