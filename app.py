from flask import Flask, request, jsonify, send_file, render_template
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
import requests
import io

app = Flask(__name__)

API_KEY = 'AIzaSyA1BeyHTGLVVQGWJD7tshBNFGsH3kt23rI'  # Substitua pela sua chave de API do Google

# Função para buscar o place_id e outros detalhes via Google Places API
def buscar_empresa_google(nome_empresa):
    # Primeiro faz a busca pelo nome da empresa
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={nome_empresa}&key={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.json()
        
        # Se encontrar resultados, pega o place_id
        if result['results']:
            place_id = result['results'][0]['place_id']
            nome_correto = result['results'][0].get('name', nome_empresa)
            endereco = result['results'][0].get('formatted_address', 'Endereço não encontrado')

            # Agora usa o place_id para buscar mais detalhes, como o telefone
            url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_phone_number&key={API_KEY}"
            details_response = requests.get(url_details)
            if details_response.status_code == 200:
                details = details_response.json()
                telefone = details['result'].get('formatted_phone_number', 'Não encontrado')
                return nome_correto, telefone, endereco

    return nome_empresa, 'Não encontrado', 'Endereço não encontrado'

# Função para gerar a planilha com formatação
def gerar_planilha(empresas):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Empresas'

    # Estilo de Cabeçalho
    header_fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    header_alignment = Alignment(horizontal="center", vertical="center")
    border_style = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    # Estilo do conteúdo
    content_fill_even = PatternFill(start_color="F7F7F7", end_color="F7F7F7", fill_type="solid")
    content_fill_odd = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    content_alignment = Alignment(horizontal="center", vertical="center")

    # Cabeçalhos
    sheet.append(['Nome da Empresa', 'Telefone', 'Endereço'])
    for col in range(1, 4):
        cell = sheet.cell(row=1, column=col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = border_style

    # Adiciona os dados das empresas
    for row_num, empresa in enumerate(empresas, start=2):
        nome_correto, telefone, endereco = buscar_empresa_google(empresa)

        sheet.append([nome_correto, telefone, endereco])

        # Aplicar bordas e cores alternadas para cada linha
        for col in range(1, 4):
            cell = sheet.cell(row=row_num, column=col)
            cell.alignment = content_alignment
            cell.border = border_style

            if row_num % 2 == 0:
                cell.fill = content_fill_even
            else:
                cell.fill = content_fill_odd

    # Ajustar o tamanho das colunas
    for col in sheet.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        sheet.column_dimensions[column].width = adjusted_width

    # Salvar a planilha em memória
    stream = io.BytesIO()
    workbook.save(stream)
    stream.seek(0)
    return stream

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gerar_planilha', methods=['POST'])
def gerar_planilha_route():
    data = request.json
    empresas = data['empresas'].split(',')
    
    planilha = gerar_planilha(empresas)
    
    # Salvar o link da planilha
    with open('planilha.xlsx', 'wb') as f:
        f.write(planilha.getbuffer())
    
    return jsonify({"link": "/download_planilha"})

@app.route('/download_planilha')
def download_planilha():
    return send_file('planilha.xlsx', as_attachment=True, download_name='empresas.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    app.run(debug=True)
