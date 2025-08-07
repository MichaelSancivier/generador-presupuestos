import streamlit as st
import pandas as pd
import json
from weasyprint import HTML, CSS
from datetime import datetime
from io import BytesIO

# ====================================================================
# Lógica de processamento y plantilla del presupuesto
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
                    <th>Descrição do Serviço</th>
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

    return
