from app import db
from datetime import datetime
import re

class Inventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_inventario = db.Column(db.String(8), nullable=False)  # Formato: DD/MM/AA
    timestamp_extracao = db.Column(db.String(19), nullable=False)  # Formato: DD/MM/AAAA HH:MM:SS
    data_importacao = db.Column(db.DateTime, default=datetime.now)
    ultima_atualizacao = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    nome_arquivo = db.Column(db.String(255), nullable=True)
    
    itens = db.relationship('ItemInventario', backref='inventario', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Inventario {self.data_inventario}>'

class ItemInventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventario_id = db.Column(db.Integer, db.ForeignKey('inventario.id'), nullable=False)
    codigo = db.Column(db.String(15), nullable=False)
    material = db.Column(db.String(100), nullable=False)
    unidade = db.Column(db.String(5), nullable=False)
    quantidade_estoque = db.Column(db.Float, nullable=False)
    quantidade_contada = db.Column(db.Float, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)
    
    # Adicionando campos para armazenar valores diretamente do arquivo
    valor_estoque_direto = db.Column(db.Float, nullable=True)
    valor_contagem_direto = db.Column(db.Float, nullable=True)
    valor_diferenca_direto = db.Column(db.Float, nullable=True)
    iv_negativo_direto = db.Column(db.Float, nullable=True)
    iv_positivo_direto = db.Column(db.Float, nullable=True)
    valor_absoluto_direto = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return f'<ItemInventario {self.codigo}>'
    
    @property
    def diferenca_quantidade(self):
        return self.quantidade_contada - self.quantidade_estoque
    
    @property
    def iv_negativo(self):
        if self.iv_negativo_direto is not None:
            return self.iv_negativo_direto
        return abs(self.diferenca_quantidade) if self.diferenca_quantidade < 0 else 0
    
    @property
    def iv_positivo(self):
        if self.iv_positivo_direto is not None:
            return self.iv_positivo_direto
        return self.diferenca_quantidade if self.diferenca_quantidade > 0 else 0
    
    @property
    def valor_absoluto_quantidade(self):
        if self.valor_absoluto_direto is not None:
            return self.valor_absoluto_direto
        return abs(self.diferenca_quantidade)
    
    @property
    def valor_estoque(self):
        if self.valor_estoque_direto is not None:
            return self.valor_estoque_direto
        return self.quantidade_estoque * self.preco_unitario
    
    @property
    def valor_contagem(self):
        if self.valor_contagem_direto is not None:
            return self.valor_contagem_direto
        return self.quantidade_contada * self.preco_unitario
    
    @property
    def diferenca_valor(self):
        if self.valor_diferenca_direto is not None:
            return self.valor_diferenca_direto
        return self.valor_contagem - self.valor_estoque
    
    @property
    def iv_negativo_valor(self):
        return abs(self.diferenca_valor) if self.diferenca_valor < 0 else 0
    
    @property
    def iv_positivo_valor(self):
        return self.diferenca_valor if self.diferenca_valor > 0 else 0
    
    @property
    def valor_absoluto_valor(self):
        return abs(self.diferenca_valor)
    
    @staticmethod
    def validar_codigo(codigo):
        # Validar padrão: 3 letras.5 números
        padrao = re.compile(r'^[A-Za-z]{3}\.\d{5}$')
        return padrao.match(codigo) is not None 