import streamlit as st
import pandas as pd
import json
from weasyprint import HTML, CSS
from datetime import datetime
from io import BytesIO

# ====================================================================
# Lógica de procesamiento y plantilla del presupuesto
# ====================================================================

# Definimos la plantilla HTML del presupuesto sin el logo
html_template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Orçamento MPFLORES</title>
    <style>
        body { font-family: sans-serif !important; font-size: 14px; margin: 0; padding: 20px; }
        .container { width: 100%; max-width: 800px; margin: auto; }
        .header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #000; padding-bottom: 10px; }
        .header h1 { color: #004c99; font-size: 24px; }
        .details { display: flex; justify-content: space-between; margin-bottom: 20px; }
        .details div { width: 48%; }
        .client-info h2, .quote-info h2 { font-size: 16px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
        .client-info p, .quote-info p { margin: 0; line-height: 1.5; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        .total-row { text-align: right; font-weight: bold; font-size: 16px; }
        .total-row td { border-top: 1px solid #000; }
        .footer { text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; }
        .footer .signature { border-top: 1px solid #000; display: inline-block; padding-top: 5px; margin-top: 20px; font-style: italic; }
        .footer p { margin: 5px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Orçamento de Serviço</h1>
        </div>
        <div class="details">
            <div class="client-info">
                <h2>CLIENTE</h2>
                <p>Nome: {client_name}</p>
                <p>Endereço: {client_address}</p>
            </div>
            <div class="quote-info">
                <h2>ORÇAMENTO</h2>
                <p>Assunto: {subject}</p>
                <p>Data: {date}</p>
                <p>Duração: {duration}</p>
                <p>Número: {quote_number}</p>
            </div>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Serviço a Realizar</th>
                    <th>Descripción del Servicio</th>
                    <th>Valor Unitário</th>
                    <th>Subtotal</th>
                </tr>
            </thead>
            <tbody>
                {service_rows}
            </tbody>
            <tfoot>
                <tr class="total-row">
                    <td colspan="3">SUBTOTAL</td>
                    <td>R$ {subtotal:.2f}</td>
                </tr>
                <tr class="total-row">
                    <td colspan="3">IMPOSTOS ({imposto_percentual:.2f}%)</td>
                    <td>R$ {impostos:.2f}</td>
                </tr>
                <tr class="total-row">
                    <td colspan="3">COMISSÃO ({comissao_percentual:.2f}%)</td>
                    <td>R$ {comissao:.2f}</td>
                </tr>
                <tr class="total-row">
                    <td colspan="3">TOTAL</td>
                    <td>R$ {total:.2f}</td>
                </tr>
            </tfoot>
        </table>
        <div class="footer">
            <p>Aprovação de Serviço</p>
            <div class="signature">
                <p>Michael Sancivier</p>
                <p>Administrador</p>
            </div>
            <p>CNPJ: ... | Tel: ... | Email: ...</p>
        </div>
    </div>
</body>
</html>
"""

def generar_html_presupuesto(data):
    """
    Función que toma los datos y los inserta en la plantilla HTML.
    """
    service_rows = ""
    for item in data['itens_servico']:
        service_rows += f"<tr><td>{item['descricao']}</td><td>{item.get('descricao_detalhada', '')}</td><td>R$ {item['valor']:.2f}</td><td>R$ {item['valor']:.2f}</td></tr>"

    return html_template.format(
        client_name=data['cliente']['nome'],
        client_address=data['cliente'].get('endereco', ''),
        subject=data['orcamento']['assunto'],
        date=data['orcamento']['data'],
        duration=data['orcamento']['duracao'],
        quote_number=data['orcamento']['numero'],
        service_rows=service_rows,
        subtotal=data['subtotal'],
        impostos=data['impostos'],
        imposto_percentual=data['imposto_percentual'],
        comissao=data['comissao'],
        comissao_percentual=data['comissao_percentual'],
        total=data['total']
    )

def generar_pdf_de_html(html_content):
    """
    Convierte el contenido HTML en un archivo PDF binario usando WeasyPrint.
    """
    buffer = BytesIO()
    HTML(string=html_content).write_pdf(buffer)
    buffer.seek(0)
    return buffer

# Función para generar un número de presupuesto único
def generar_numero_orcamento_unico():
    # Obtiene la fecha actual en formato YYYYMMDD
    fecha_actual = datetime.now().strftime("%Y%m%d")
    # Usa un contador para generar el número.
    # Nota: Este contador se reinicia cada vez que se carga la app en Streamlit Cloud.
    # Para que sea persistente, se necesitaría una base de datos.
    if 'contador' not in st.session_state:
        st.session_state.contador = 0
    st.session_state.contador += 1
    
    # Formato del número (ej: MPF-20250806-001)
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
    
    # El número de presupuesto ahora se genera automáticamente
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

    # Llamar a la herramienta de generación de HTML (nuestra función de Python)
    try:
        html_content = generar_html_presupuesto(datos_agente)
        st.success("Presupuesto generado con éxito.")
        
        # Previsualización
        st.header("Previsualización del Presupuesto")
        st.components.v1.html(html_content, height=800, scrolling=True)

        # Generar el PDF para descarga
        pdf_data = generar_pdf_de_html(html_content)
        st.download_button(
            label="📥 Descargar PDF",
            data=pdf_data,
            file_name=f"presupuesto-{cliente_nombre}-{numero_orcamento}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Ocorreu um error ao gerar o orçamento: {e}")
