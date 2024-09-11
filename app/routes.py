from flask import Blueprint, request, render_template, jsonify
import pandas as pd

# Define the blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload():
    print("upload")
    if 'file1' not in request.files or 'file2' not in request.files:
        return "Please upload both files", 400
    
    file1 = request.files['file1']
    file2 = request.files['file2']

    # Load Excel files
    excel1 = pd.ExcelFile(file1)
    excel2 = pd.ExcelFile(file2)
    
    # Get sheet names
    sheets1 = excel1.sheet_names
    sheets2 = excel2.sheet_names
    print(f"Sheets1: {sheets1}, Sheets2: {sheets2}")  # Debugging
    return jsonify({'sheets1': sheets1, 'sheets2': sheets2})

@main.route('/get_columns', methods=['POST'])
def get_columns():
    file = request.files['file']
    sheet_name = request.form['sheet']

    excel = pd.ExcelFile(file)
    df = pd.read_excel(excel, sheet_name=sheet_name)

    columns = df.columns.tolist()
    return jsonify({'columns': columns})

def get_excel_column_letter(col_num):
    """Função auxiliar para converter o número da coluna em uma letra no estilo Excel."""
    col_letter = ''
    while col_num > 0:
        col_num, remainder = divmod(col_num - 1, 26)
        col_letter = chr(65 + remainder) + col_letter
    return col_letter


@main.route('/compare', methods=['POST'])
def compare():
    file1 = request.files['file1']
    sheet1 = request.form['sheet1']
    column1 = request.form['column1']

    file2 = request.files['file2']
    sheet2 = request.form['sheet2']
    column2 = request.form['column2']

    # Carregar as abas selecionadas dos arquivos
    df1 = pd.read_excel(file1, sheet_name=sheet1)
    df2 = pd.read_excel(file2, sheet_name=sheet2)

    # Verificar se as colunas existem nas planilhas
    if column1 not in df1.columns or column2 not in df2.columns:
        return jsonify({
            'error': f"A coluna {column1} não foi encontrada na planilha 1 ou a coluna {column2} não foi encontrada na planilha 2."
        })

    # Comparar o número de linhas das duas colunas
    if df1[column1].shape[0] != df2[column2].shape[0]:
        return jsonify({
            'error': f"As colunas têm números diferentes de linhas e não podem ser comparadas.\n"
                     f"{column1} tem {df1[column1].shape[0]} linhas e {column2} tem {df2[column2].shape[0]} linhas."
        })

    # Lista para armazenar as diferenças
    differences = []

    # Comparar célula a célula nas colunas
    for row in range(df1[column1].shape[0]):
        cell1 = df1.iloc[row][column1]
        cell2 = df2.iloc[row][column2]

        # Ignora diferenças onde ambas as células são NaN
        if pd.isna(cell1) and pd.isna(cell2):
            continue

        if cell1 != cell2:
            # Obter o nome da célula no estilo Excel (ex: A5, B7)
            cell_name1 = f"{get_excel_column_letter(df1.columns.get_loc(column1) + 1)}{row + 1}"
            cell_name2 = f"{get_excel_column_letter(df2.columns.get_loc(column2) + 1)}{row + 1}"
            # Adicionar a diferença na lista
            differences.append(
                f"Diferença nas células {cell_name1} (Planilha1) e {cell_name2} (Planilha2): Planilha1 = '{cell1}' vs Planilha2 = '{cell2}'"
            )

    # Se não houver diferenças
    if not differences:
        return jsonify({'message': 'As colunas selecionadas são idênticas.'})

    # Retornar as diferenças como uma lista de strings
    return jsonify({'differences': differences})

def compare():
    file1 = request.files['file1']
    sheet1 = request.form['sheet1']
    column1 = request.form['column1']

    file2 = request.files['file2']
    sheet2 = request.form['sheet2']
    column2 = request.form['column2']

    # Carregar as abas selecionadas dos arquivos
    df1 = pd.read_excel(file1, sheet_name=sheet1)
    df2 = pd.read_excel(file2, sheet_name=sheet2)

    # Realiza a comparação entre as colunas usando merge para identificar as diferenças
    merged_df = pd.merge(
        df1[[column1]], df2[[column2]], 
        how='outer', left_on=column1, right_on=column2, 
        indicator=True
    )

    # Adicionar uma coluna para indicar onde o valor foi encontrado: 'both', 'left_only', 'right_only'
    merged_df['status'] = merged_df['_merge'].map({
        'left_only': f'Somente em {column1}', 
        'right_only': f'Somente em {column2}', 
        'both': 'Em ambos'
    })

    # Selecionar as colunas de interesse para exibição
    result_df = merged_df[[column1, column2, 'status']]

    # Converte o DataFrame para uma tabela HTML
    result_html = result_df.to_html(index=False)

    # Retorna o HTML da tabela para o frontend
    return jsonify({'html_table': result_html})