import concurrent.futures
from flask import Flask, request, jsonify, send_file, render_template
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
import requests
import io
import os

app = Flask(__name__)

API_KEY = 'AIzaSyBzEyajtT9LSoBgF9BI_ui6bPK4R-ICmKU'

# Função para buscar o place_id e outros detalhes via Google Places API
def buscar_empresa_google(nome_empresa):
    if not isinstance(nome_empresa, str):
        nome_empresa = str(nome_empresa)
    
    nome_empresa_corrigido = nome_empresa.strip().replace('  ', ' ')  # Remove espaços duplos
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={nome_empresa_corrigido}&key={API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)  # Adiciona timeout
        if response.status_code == 200:
            result = response.json()
            if result['results']:
                place_id = result['results'][0]['place_id']
                nome_correto = result['results'][0].get('name', nome_empresa_corrigido)
                endereco = result['results'][0].get('formatted_address', 'Endereço não encontrado')

                # Busca mais detalhes usando o place_id, como o telefone
                url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_phone_number&key={API_KEY}"
                details_response = requests.get(url_details, timeout=10)  # Adiciona timeout na requisição de detalhes
                if details_response.status_code == 200:
                    details = details_response.json()
                    telefone = details['result'].get('formatted_phone_number', 'Não encontrado')
                    return nome_correto, telefone, endereco
            else:
                print(f"Empresa não encontrada: {nome_empresa}")
    except requests.exceptions.ReadTimeout:
        print(f"Timeout ao buscar empresa: {nome_empresa}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar empresa: {nome_empresa}, erro: {e}")
    
    return nome_empresa, 'Não encontrado', 'Endereço não encontrado'

# Função para buscar empresas em paralelo
def buscar_empresas_em_paralelo(empresas):
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:  # Reduz max_workers para evitar sobrecarga
        results = list(executor.map(buscar_empresa_google, empresas))
    return results

# Função para ler a planilha enviada e gerar uma nova planilha com os dados completos
def gerar_planilha_com_dados(file_path):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active

    empresas = []
    for row in sheet.iter_rows(min_row=2, max_col=1, values_only=True):
        empresas.append(row[0])

    resultados = buscar_empresas_em_paralelo(empresas)

    novo_workbook = openpyxl.Workbook()
    novo_sheet = novo_workbook.active
    novo_sheet.title = 'Empresas Atualizadas'

    header_fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    header_alignment = Alignment(horizontal="center", vertical="center")
    border_style = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    content_fill_even = PatternFill(start_color="F7F7F7", end_color="F7F7F7", fill_type="solid")
    content_fill_odd = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    content_alignment = Alignment(horizontal="center", vertical="center")

    novo_sheet.append(['Nome da Empresa', 'Telefone', 'Endereço'])
    for col in range(1, 4):
        cell = novo_sheet.cell(row=1, column=col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = border_style

    for row_num, resultado in enumerate(resultados, start=2):
        nome_correto, telefone, endereco = resultado
        novo_sheet.append([nome_correto, telefone, endereco])
        for col in range(1, 4):
            cell = novo_sheet.cell(row=row_num, column=col)
            cell.alignment = content_alignment
            cell.border = border_style
            cell.fill = content_fill_even if row_num % 2 == 0 else content_fill_odd

    for col in novo_sheet.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        novo_sheet.column_dimensions[column].width = adjusted_width

    stream = io.BytesIO()
    novo_workbook.save(stream)
    stream.seek(0)
    return stream

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_planilha', methods=['POST'])
def upload_planilha():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']

    # Criar o diretório uploads se não existir
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    planilha = gerar_planilha_com_dados(file_path)
    os.remove(file_path)

    # Garantir que o diretório para salvar o arquivo existe
    os.makedirs(os.path.dirname(os.path.abspath('planilha_atualizada.xlsx')), exist_ok=True)
    
    with open('planilha_atualizada.xlsx', 'wb') as f:
        f.write(planilha.getbuffer())
    
    return jsonify({"link": "/download_planilha"})

@app.route('/download_planilha')
def download_planilha():
    return send_file('planilha_atualizada.xlsx', as_attachment=True, download_name='empresas_atualizadas.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# Modificação para produção no Render
if __name__ == '__main__':
    # Verifica se estamos em ambiente de produção
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)