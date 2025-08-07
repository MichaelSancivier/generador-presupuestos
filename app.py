import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

# ====================================================================
# Lógica de processamento y plantilla del presupuesto (com FPDF)
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
    return pdf.output(dest='S').encode('latin1')

# Función para generar un número de presupuesto único
def generar_numero_orcamento_unico():
    fecha_actual = datetime.now().strftime("%Y%m%d")
    if 'contador' not in st.session_state:
        st.session_state.contador = 0
    st.session_state.contador += 1
    return f"MPF-{fecha_actual}-{st.session_state.contador:03d}"

# ====================================================================
# Interfaz de Usuario de Streamlit
# ====================================================================

st.set_page_config(page_title="Generador de Presupuestos MPFLORES", layout="wide")
st.title("👨‍💼 Generador de Presupuestos")
st.markdown("Crea un presupuesto profesional de forma automática para tus clientes.")

# === Formulario de entrada ===
with st.form("formulario_presupuesto"):
    st.header("Información del Cliente y del Presupuesto")
    cliente_nombre = st.text_input("Nombre del Cliente", "Missão Curitiba")
    cliente_endereco = st.text_input("Dirección del Cliente", "Rua Rio Grande do Sul, 800")
    assunto = st.text_input("Asunto del Presupuesto", "Orçamento Limpeza Profunda de Sobrado")
    duracao = st.text_input("Duración Estimada", "8 horas")
    data = st.date_input("Fecha")
    
    numero_orcamento = generar_numero_orcamento_unico()
    st.info(f"Número de Presupuesto: **{numero_orcamento}**")
    
    st.header("Servicios")
    servicios = st.data_editor(
        pd.DataFrame([
            {"descricao": "Limpieza y higienización de sofá", "valor": 350.00},
            {"descricao": "Limpeza de ventanas, pisos, etc.", "valor": 750.00},
        ]),
        num_rows="dynamic",
        use_container_width=True
    )
    
    st.header("Cálculos Adicionales")
    imposto_percentual = st.number_input("Porcentaje de Impuestos (%)", min_value=0.0, max_value=100.0, value=12.0)
    comissao_percentual = st.number_input("Porcentaje de Comisión (%)", min_value=0.0, max_value=100.0, value=3.0)

    submitted = st.form_submit_button("Generar y Previsualizar Presupuesto")

if submitted:
    # Lógica de cálculo
    subtotal = servicios['valor'].sum()
    impostos = subtotal * (imposto_percentual / 100)
    comissao = subtotal * (comissao_percentual / 100)
    total = subtotal + impostos + comissao

    # Ensamblar el objeto JSON para la herramienta
    datos_agente = {
        "cliente": {"nome": cliente_nombre, "endereco": cliente_endereco},
        "orcamento": {
            "assunto": assunto,
            "duracao": duracao,
            "data": str(data),
            "numero": numero_orcamento
        },
        "itens_servico": servicios.to_dict('records'),
        "subtotal": subtotal,
        "impostos": impostos,
        "imposto_percentual": imposto_percentual,
        "comissao": comissao,
        "comissao_percentual": comissao_percentual,
        "total": total
    }

    # Gerar o PDF
    try:
        pdf_bytes = gerar_pdf_orcamento(datos_agente)
        st.success("Presupuesto generado con éxito.")
        
        # A pré-visualização HTML foi removida, pois fpdf2 não a suporta
        # Agora você pode baixar o PDF diretamente.

        st.download_button(
            label="📥 Descargar PDF",
            data=pdf_bytes,
            file_name=f"presupuesto-{cliente_nombre}-{numero_orcamento}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Ocorreu um erro ao gerar o orçamento: {e}")
