import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

# ====================================================================
# Lógica de procesamiento y plantilla del presupuesto (com FPDF)
# ====================================================================

def gerar_pdf_orcamento(data):
    pdf = FPDF(unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    
    # Adicionando o cabeçalho
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 10, 'Orçamento de Serviço', 0, 1, 'C')
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # Detalhes do cliente e orçamento
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, 'CLIENTE', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 6, f"Nome: {data['cliente']['nome']}", 0, 1)
    pdf.cell(0, 6, f"Endereço: {data['cliente'].get('endereco', '')}", 0, 1)
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, 'ORÇAMENTO', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 6, f"Assunto: {data['orcamento']['assunto']}", 0, 1)
    pdf.cell(0, 6, f"Data: {data['orcamento']['data']}", 0, 1)
    pdf.cell(0, 6, f"Duração: {data['orcamento']['duracao']}", 0, 1)
    pdf.cell(0, 6, f"Número: {data['orcamento']['numero']}", 0, 1)
    pdf.ln(10)

    # Tabela de serviços
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(150, 10, 'Serviço a Realizar', 1, 0)
    pdf.cell(40, 10, 'Valor Unitário', 1, 1, 'R')
    
    pdf.set_font('Arial', '', 12)
    for item in data['itens_servico']:
        pdf.cell(150, 8, item['descricao'], 1, 0)
        pdf.cell(40, 8, f"R$ {item['valor']:.2f}", 1, 1, 'R')
    pdf.ln(10)
    
    # Totais
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(150, 8, 'SUBTOTAL', 0, 0, 'R')
    pdf.cell(40, 8, f"R$ {data['subtotal']:.2f}", 0, 1, 'R')
    
    pdf.cell(150, 8, f"IMPOSTOS ({data['imposto_percentual']:.2f}%)", 0, 0, 'R')
    pdf.cell(40, 8, f"R$ {data['impostos']:.2f}", 0, 1, 'R')

    pdf.cell(150, 8, f"COMISSÃO ({data['comissao_percentual']:.2f}%)", 0, 0, 'R')
    pdf.cell(40, 8, f"R$ {data['comissao']:.2f}", 0, 1, 'R')
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(150, 10, 'TOTAL', 0, 0, 'R')
    pdf.cell(40, 10, f"R$ {data['total']:.2f}", 0, 1, 'R')
    
    # Footer
    pdf.ln(20)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 5, 'Aprovação de Serviço', 0, 1, 'C')
    pdf.cell(0, 5, '-' * 40, 0, 1, 'C')
    pdf.cell(0, 5, 'Michael Sancivier', 0, 1, 'C')
    pdf.cell(0, 5, 'Administrador', 0, 1, 'C')
    
    # Retorna o PDF como bytes
    return pdf.output(dest='S')

# Función para generar un número de presupuesto único
def
