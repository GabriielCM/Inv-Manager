from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from app import db
from app.models.models import Inventario, ItemInventario
from app.utils.parser import InventarioParser
import os
from werkzeug.utils import secure_filename
import pandas as pd
import tempfile
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    inventarios = Inventario.query.order_by(Inventario.data_importacao.desc()).all()
    return render_template('index.html', inventarios=inventarios)

@main_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(request.url)
        
        if file and file.filename.endswith('.lst') or file.filename.endswith('.txt'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', filename)
            
            # Verificar se o diretório uploads existe
            upload_dir = os.path.dirname(file_path)
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
                
            file.save(file_path)
            
            try:
                # Processar o arquivo
                parser = InventarioParser(file_path)
                inventario, itens = parser.processar_arquivo()
                
                # Verificar se já existe um inventário com a mesma data e hora de extração
                existing_inventory = Inventario.query.filter_by(
                    data_inventario=inventario.data_inventario,
                    timestamp_extracao=inventario.timestamp_extracao
                ).first()
                
                if existing_inventory:
                    flash(f'Já existe um inventário com a data {inventario.data_inventario} e hora de extração {inventario.timestamp_extracao}', 'warning')
                    return redirect(url_for('main.index'))
                
                # Salvar no banco de dados
                db.session.add(inventario)
                db.session.flush()  # Para obter o ID do inventário
                
                for item in itens:
                    item.inventario_id = inventario.id
                    db.session.add(item)
                
                db.session.commit()
                flash(f'Arquivo processado com sucesso. {len(itens)} itens importados.', 'success')
                return redirect(url_for('main.view_inventario', id=inventario.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao processar arquivo: {str(e)}', 'danger')
                return redirect(request.url)
    
    return render_template('upload.html')

@main_bp.route('/inventario/<int:id>')
def view_inventario(id):
    inventario = Inventario.query.get_or_404(id)
    
    # Filtros opcionais
    codigo_filtro = request.args.get('codigo', '')
    material_filtro = request.args.get('material', '')
    apenas_diferencas = request.args.get('apenas_diferencas', '')
    
    query = ItemInventario.query.filter_by(inventario_id=id)
    
    if codigo_filtro:
        query = query.filter(ItemInventario.codigo.like(f'%{codigo_filtro}%'))
    
    if material_filtro:
        query = query.filter(ItemInventario.material.like(f'%{material_filtro}%'))
    
    # Aplicar filtro de apenas diferenças
    if apenas_diferencas == 'true':
        query = query.filter(ItemInventario.quantidade_estoque != ItemInventario.quantidade_contada)
    
    itens = query.all()
    
    # Calcular totais
    total_estoque = sum(item.quantidade_estoque for item in itens)
    total_contagem = sum(item.quantidade_contada for item in itens)
    total_diferenca = total_contagem - total_estoque
    total_iv_negativo = sum(item.iv_negativo for item in itens)
    total_iv_positivo = sum(item.iv_positivo for item in itens)
    total_val_absoluto = sum(item.valor_absoluto_quantidade for item in itens)
    
    total_valor_estoque = sum(item.valor_estoque for item in itens)
    total_valor_contagem = sum(item.valor_contagem for item in itens)
    total_valor_diferenca = total_valor_contagem - total_valor_estoque
    total_valor_iv_negativo = sum(item.iv_negativo_valor for item in itens)
    total_valor_iv_positivo = sum(item.iv_positivo_valor for item in itens)
    total_valor_absoluto = sum(item.valor_absoluto_valor for item in itens)
    
    totais = {
        'estoque': total_estoque,
        'contagem': total_contagem,
        'diferenca': total_diferenca,
        'iv_negativo': total_iv_negativo,
        'iv_positivo': total_iv_positivo,
        'val_absoluto': total_val_absoluto,
        'valor_estoque': total_valor_estoque,
        'valor_contagem': total_valor_contagem,
        'valor_diferenca': total_valor_diferenca,
        'valor_iv_negativo': total_valor_iv_negativo,
        'valor_iv_positivo': total_valor_iv_positivo,
        'valor_absoluto': total_valor_absoluto
    }
    
    return render_template('view_inventario.html', inventario=inventario, itens=itens, totais=totais)

@main_bp.route('/inventario/<int:id>/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(id, item_id):
    inventario = Inventario.query.get_or_404(id)
    item = ItemInventario.query.get_or_404(item_id)
    
    if request.method == 'POST':
        try:
            quantidade_contada = float(request.form['quantidade_contada'].replace(',', '.'))
            item.quantidade_contada = quantidade_contada
            inventario.ultima_atualizacao = datetime.now()
            db.session.commit()
            flash('Item atualizado com sucesso', 'success')
            return redirect(url_for('main.view_inventario', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar item: {str(e)}', 'danger')
    
    return render_template('edit_item.html', inventario=inventario, item=item)

@main_bp.route('/inventario/<int:id>/delete_item/<int:item_id>', methods=['POST'])
def delete_item(id, item_id):
    item = ItemInventario.query.get_or_404(item_id)
    inventario = Inventario.query.get_or_404(id)
    
    try:
        db.session.delete(item)
        inventario.ultima_atualizacao = datetime.now()
        db.session.commit()
        flash('Item excluído com sucesso', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir item: {str(e)}', 'danger')
    
    return redirect(url_for('main.view_inventario', id=id))

@main_bp.route('/inventario/<int:id>/delete', methods=['POST'])
def delete_inventario(id):
    inventario = Inventario.query.get_or_404(id)
    
    try:
        db.session.delete(inventario)
        db.session.commit()
        flash('Inventário excluído com sucesso', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir inventário: {str(e)}', 'danger')
    
    return redirect(url_for('main.index'))

@main_bp.route('/inventario/<int:id>/export/<format>')
def export_inventario(id, format):
    inventario = Inventario.query.get_or_404(id)
    itens = ItemInventario.query.filter_by(inventario_id=id).all()
    
    # Criar DataFrame com os dados dos itens
    data = []
    for item in itens:
        data.append({
            'Código': item.codigo,
            'Material': item.material,
            'Unidade': item.unidade,
            'Quantidade Estoque': item.quantidade_estoque,
            'Quantidade Contada': item.quantidade_contada,
            'Diferença': item.diferenca_quantidade,
            'IV-': item.iv_negativo,
            'IV+': item.iv_positivo,
            'Val. Absoluto': item.valor_absoluto_quantidade,
            'Valor Estoque': item.valor_estoque,
            'Valor Contagem': item.valor_contagem,
            'Valor Diferença': item.diferenca_valor,
            'Valor IV-': item.iv_negativo_valor,
            'Valor IV+': item.iv_positivo_valor,
            'Valor Absoluto': item.valor_absoluto_valor,
            'Preço Unitário': item.preco_unitario
        })
    
    df = pd.DataFrame(data)
    
    # Exportar no formato solicitado
    if format == 'excel':
        # Criar arquivo Excel temporário
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp:
            temp_path = temp.name
        
        # Salvar DataFrame como Excel
        df.to_excel(temp_path, index=False, sheet_name=f'Inventário {inventario.data_inventario}')
        
        # Retornar arquivo para download
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f'Inventario_{inventario.data_inventario.replace("/", "-")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    elif format == 'csv':
        # Criar arquivo CSV temporário
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp:
            temp_path = temp.name
        
        # Salvar DataFrame como CSV
        df.to_csv(temp_path, index=False, sep=';', decimal=',')
        
        # Retornar arquivo para download
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f'Inventario_{inventario.data_inventario.replace("/", "-")}.csv',
            mimetype='text/csv'
        )
    
    # Formato txt - emular o formato original do arquivo lst
    elif format == 'txt':
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w', encoding='utf-8') as temp:
            temp_path = temp.name
            
            # Escrever cabeçalho
            temp.write(f"CRISTOFOLI EQUIP BIOSSEGURANCA LTDA \n")
            temp.write(f"esp1107   RELATORIO DE MATERIAIS INVENTARIADOS  -  WMS                   FL.   1\n")
            temp.write(f"                                         EXTRAIDO EM {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} HRS.\n")
            temp.write("                                      DATA    |                    QUANTIDADE                                                     ||                         VALOR                                                                 |PRE     |\n")
            temp.write("CODIGO          MATERIAL          UN. INVENT. |ESTOQUE       CONTAGEM      DIFERENCA     IV-           IV+           VAL. ABSOLUTO||ESTOQUE         CONTAGEM        DIFERENCA       IV-             IV+             VAL. ABSOLUTO  |UNIT.   |\n")
            temp.write("--------------- ----------------- --- --------|------------- ------------- ------------- ------------- ------------- -------------||--------------- --------------- --------------- --------------- --------------- ---------------|--------|\n")
            
            # Escrever dados
            for item in itens:
                # Formatação dos valores para o formato do arquivo .lst
                linha = f"{item.codigo:<15} {item.material:<15} {item.unidade:<3} {inventario.data_inventario:>8} "
                linha += f"{item.quantidade_estoque:>13,.2f} {item.quantidade_contada:>13,.2f} {item.diferenca_quantidade:>13,.2f} "
                linha += f"{item.iv_negativo:>13,.2f} {item.iv_positivo:>13,.2f} {item.valor_absoluto_quantidade:>13,.2f} "
                linha += f"{item.valor_estoque:>15,.2f} {item.valor_contagem:>15,.2f} {item.diferenca_valor:>15,.2f} "
                linha += f"{item.iv_negativo_valor:>15,.2f} {item.iv_positivo_valor:>15,.2f} {item.valor_absoluto_valor:>15,.2f} "
                linha += f"{item.preco_unitario:>8,.2f}\n"
                
                temp.write(linha)
            
            # Linha separadora
            temp.write(" -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
            
            # Linha de totais
            total_estoque = sum(item.quantidade_estoque for item in itens)
            total_contagem = sum(item.quantidade_contada for item in itens)
            total_diferenca = total_contagem - total_estoque
            total_iv_negativo = sum(item.iv_negativo for item in itens)
            total_iv_positivo = sum(item.iv_positivo for item in itens)
            total_val_absoluto = sum(item.valor_absoluto_quantidade for item in itens)
            
            total_valor_estoque = sum(item.valor_estoque for item in itens)
            total_valor_contagem = sum(item.valor_contagem for item in itens)
            total_valor_diferenca = total_valor_contagem - total_valor_estoque
            total_valor_iv_negativo = sum(item.iv_negativo_valor for item in itens)
            total_valor_iv_positivo = sum(item.iv_positivo_valor for item in itens)
            total_valor_absoluto = sum(item.valor_absoluto_valor for item in itens)
            
            linha_total = f"TOTAL                                                   {total_estoque:>13,.2f} {total_contagem:>13,.2f} {total_diferenca:>13,.2f} "
            linha_total += f"{total_iv_negativo:>13,.2f} {total_iv_positivo:>13,.2f} {total_val_absoluto:>13,.2f} "
            linha_total += f"{total_valor_estoque:>15,.2f} {total_valor_contagem:>15,.2f} {total_valor_diferenca:>15,.2f} "
            linha_total += f"{total_valor_iv_negativo:>15,.2f} {total_valor_iv_positivo:>15,.2f} {total_valor_absoluto:>15,.2f}\n"
            
            temp.write(linha_total)
        
        # Retornar arquivo para download
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f'Inventario_{inventario.data_inventario.replace("/", "-")}.txt',
            mimetype='text/plain'
        )
    
    else:
        flash(f'Formato de exportação inválido: {format}', 'danger')
        return redirect(url_for('main.view_inventario', id=id)) 