import hashlib
import pandas as pd
import streamlit as st
import PyPDF2
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import io

# Função para gerar hash de uma string
def gerar_hash(conteudo):
    return hashlib.sha256(conteudo.encode()).hexdigest()

# Função para ler o conteúdo de um arquivo PDF
def ler_pdf(arquivo):
    conteudo = ""
    try:
        with io.BytesIO(arquivo.read()) as pdf_buffer:
            pdf_reader = PyPDF2.PdfReader(pdf_buffer)
            for page in pdf_reader.pages:
                texto = page.extract_text()
                if texto:
                    conteudo += texto + "\n"
    except Exception as e:
        st.error(f"Erro ao ler o PDF: {e}")
    return conteudo.strip()

# Função para carregar múltiplos arquivos e gerar os hashes
def carregar_arquivos(arquivos):
    resultados = []
    for arquivo in arquivos:
        conteudo = None
        if arquivo.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(arquivo)
            conteudo = df.to_string(index=False)
        elif arquivo.name.endswith('.txt'):
            conteudo = arquivo.read().decode("utf-8")
        elif arquivo.name.endswith('.pdf'):
            conteudo = ler_pdf(arquivo)

        if conteudo:
            hash_gerado = gerar_hash(conteudo)
            resultados.append((arquivo.name, hash_gerado))
    return resultados

# Função para gerar e retornar o PDF com os hashes
def gerar_pdf_tabela(dados):
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1, bottomMargin=1 * cm, leftMargin=1 * cm, rightMargin=1 * cm)

    dados_tabela = [["Nome do Arquivo", "Hash Gerado (SHA-256)"]]
    
    # Quebra o nome do arquivo em múltiplas linhas se for muito longo
    max_len = 55
    for nome, hash_code in dados:
        nome_quebrado = '\n'.join([nome[i:i+max_len] for i in range(0, len(nome), max_len)])
        dados_tabela.append([nome_quebrado, hash_code])

    tabela = Table(dados_tabela, colWidths=[10*cm, 10*cm])
    estilo_tabela = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('LEADING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ])
    tabela.setStyle(estilo_tabela)

    data_atual = datetime.now().strftime("%d/%m/%Y")
    hora_atual = datetime.now().strftime("%H:%M:%S")
    mensagem = f'A tabela contendo o código hash referente a cada arquivo foi gerada na data "{data_atual}" às "{hora_atual}".'
    estilo = getSampleStyleSheet()["Normal"]
    paragrafo_mensagem = Paragraph(mensagem, estilo)

    cabecalho_imagem = Image("cabeçalho_pol_gov.jpg", width=22 * cm, height=3 * cm)

    elementos = [cabecalho_imagem, paragrafo_mensagem, tabela]

    try:
        pdf.build(elementos)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Erro ao gerar o PDF: {e}")
        return None

# Interface Streamlit
st.title("Leitor de Arquivos e Gerador de Hash")
st.write("Carregue seus arquivos para gerar os hashes correspondentes.")

arquivos_upload = st.file_uploader("Escolha os arquivos", type=["xlsx", "xls", "txt", "pdf"], accept_multiple_files=True)
if arquivos_upload:
    resultados = carregar_arquivos(arquivos_upload)
    if resultados:
        st.write("**Resultados:**")
        for nome_arquivo, hash_gerado in resultados:
            st.write(f"{nome_arquivo}: {hash_gerado}")

        # Gerar PDF automaticamente
        pdf_buffer = gerar_pdf_tabela(resultados)
        if pdf_buffer:
            st.success("PDF gerado com sucesso!")

            # Campo de entrada para o nome do arquivo
            nome_arquivo = st.text_input("Digite o nome do arquivo para download", value="hashes")

            # Botão para baixar o PDF com o nome especificado pelo usuário
            st.download_button("Baixar PDF com Hashes", pdf_buffer, file_name=f"{nome_arquivo}.pdf", mime='application/pdf')
    else:
        st.warning("Nenhum arquivo válido carregado.")
