from PyPDF2 import PdfReader, PdfWriter
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Função para dividir o PDF
def split_pdf(input_pdf_path, output_folder):
    try:
        # Lendo o arquivo PDF
        reader = PdfReader(input_pdf_path)

        # Certifique-se de que o diretório de saída existe
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Itera sobre as páginas do PDF
        for page_number, page in enumerate(reader.pages, start=1):
            writer = PdfWriter()
            writer.add_page(page)

            # Definindo o nome do arquivo de saída para cada página
            output_pdf_path = os.path.join(output_folder, f"page_{page_number}.pdf")

            # Salvando a página como um novo arquivo PDF
            with open(output_pdf_path, 'wb') as output_file:
                writer.write(output_file)
        
        return True, len(reader.pages)
    except Exception as e:
        return False, str(e)

# Rota para a página inicial
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return "Nenhum arquivo enviado", 400

        pdf_file = request.files['pdf_file']
        if pdf_file.filename == '':
            return "Nenhum arquivo selecionado", 400

        # Caminho completo para salvar o arquivo enviado
        input_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
        pdf_file.save(input_pdf_path)

        # Diretório de saída
        output_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'output')

        # Dividir o PDF
        success, result = split_pdf(input_pdf_path, output_folder)
        
        if success:
            return redirect(url_for('results', total_pages=result))
        else:
            return f"Erro ao processar o arquivo: {result}", 500

    return render_template('index.html')

# Rota para mostrar os resultados
@app.route('/results')
def results():
    total_pages = request.args.get('total_pages', 0, type=int)
    output_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'output')
    file_list = [f for f in os.listdir(output_folder) if f.endswith('.pdf')]
    return render_template('results.html', total_pages=total_pages, files=file_list)

# Rota para servir os arquivos gerados
@app.route('/uploads/output/<filename>')
def download_file(filename):
    output_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'output')
    return send_from_directory(output_folder, filename)

if __name__ == '__main__':
    # Certifique-se de que o diretório de uploads existe
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
