import streamlit as st
import pandas as pd
import json
from weasyprint import HTML, CSS
import base64
from io import BytesIO
from datetime import datetime

# ====================================================================
# Lógica de procesamiento y plantilla del presupuesto
# ====================================================================

# Definimos la plantilla HTML del presupuesto
# Esta plantilla es crucial para el diseño final del PDF
# Puedes editar este código HTML y CSS para que coincida con tu diseño
html_template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Orçamento MPFLORES</title>
    <style>
        body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 14px; margin: 0; padding: 20px; }
        .container { width: 100%; max-width: 800px; margin: auto; }
        .header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #000; padding-bottom: 10px; }
        .header h1 { color: #004c99; font-size: 24px; }
        .header img { max-width: 150px; }
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
            <img src="data:image/png;base64,{logo_base64}" alt="Logo MPFLORES">
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

# Simulamos el logo en Base64 para que aparezca en el HTML
# Reemplaza esta cadena con el código Base64 de tu logo
logo_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAB4AAAAQ4CAYAAADo08FDAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAE22lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSfvu78nIGlkPSdXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQnPz4KPHg6eG1wbWV0YSB4bWxuczp4PSdhZG9iZTpuczptZXRhLyc+CjxyZGY6UkRGIHhtbG5zOnJkZj0naHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyc+CgogPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9JycKICB4bWxuczpBdHRyaWI9J2h0dHA6Ly9ucy5hdHRyaWJ1dGlvbi5jb20vYWRzLzEuMC8nPgogIDxBdHRyaWI6QWRzPgogICA8cmRmOlNlcT4KICAgIDxyZGY6bGkgcmRmOnBhcnNlVHlwZT0nUmVzb3VyY2UnPgogICAgIDxBdHRyaWI6Q3JlYXRlZD4yMDI1LTA4LTA3PC9BdHRyaWI6Q3JlYXRlZD4KICAgICA8QXR0cmliOkV4dElkPmQ1Yjc3NGFiLWI3NTYtNDBlZS05NmJhLTEzYmRhZmU5OGNjMDwvQXR0cmliOkV4dElkPgogICAgIDxBdHRyaWI6RmJJZD41MjUyNjU5MTQxNzk1ODA8L0F0dHJpYjpGYklkPgogICAgIDxBdHRyaWI6VG91Y2hUeXBlPjI8L0F0dHJpYjpUb3VjaFR5cGU+CiAgICA8L3JkZjpsaT4KICAgPC9yZGY6U2VxPgogIDwvQXR0cmliOkFkcz4KIDwvcmRmOkRlc2NyaXB0aW9uP
