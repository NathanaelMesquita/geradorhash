import hashlib
import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
from datetime import datetime
import PyPDF2
import os
import sys

# Função para obter o caminho correto do arquivo de imagem
def obter_caminho_imagem(nome_imagem):
    if getattr(sys, 'frozen', False):  # Se o programa estiver congelado
        caminho = os.path.join(sys._MEIPASS, nome_imagem)
    else:  # Se estiver em execução normal
        caminho = nome_imagem
    return caminho

# Função para gerar hash de uma string
def gerar_hash(conteudo):
    return hashlib.sha256(conteudo.encode()).hexdigest()

# Função para carregar múltiplos arquivos e gerar os hashes
def carregar_arquivos():
    caminhos_arquivos = filedialog.askopenfilenames(filetypes=[("Todos os arquivos", "*.xlsx *.xls *.txt *.pdf")])
    if caminhos_arquivos:
        try:
            for caminho_arquivo in caminhos_arquivos:
                if caminho_arquivo.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(caminho_arquivo)
                    conteudo = df.to_string()
                elif caminho_arquivo.endswith('.txt'):
                    with open(caminho_arquivo, 'r') as file:
                        conteudo = file.read()
                elif caminho_arquivo.endswith('.pdf'):
                    conteudo = ler_pdf(caminho_arquivo)
                    if not conteudo:
                        messagebox.showerror("Erro", "Não foi possível extrair texto do PDF.")
                        continue
                else:
                    conteudo = None

                if conteudo:
                    hash_gerado = gerar_hash(conteudo)
                    nome_arquivo = os.path.basename(caminho_arquivo)  # Obtém apenas o nome do arquivo
                    adicionar_na_tabela(nome_arquivo, hash_gerado)

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar os arquivos: {e}")

# Função para ler o conteúdo de um arquivo PDF
def ler_pdf(caminho_arquivo):
    conteudo = ""
    try:
        with open(caminho_arquivo, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                texto = page.extract_text()
                if texto:
                    conteudo += texto + "\n"
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível ler o PDF: {e}")
    return conteudo.strip()

# Função para adicionar o resultado na tabela
def adicionar_na_tabela(nome_arquivo, hash_gerado):
    tree.insert("", "end", values=(nome_arquivo, hash_gerado))

# Função para gerar um PDF com a tabela de hashes
# Importação do Paragraph para adicionar o texto da mensagem
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Função para gerar um PDF com a tabela de hashes
def gerar_pdf_tabela():
    caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if caminho_arquivo:
        try:
            # Criação do documento PDF
            pdf = SimpleDocTemplate(caminho_arquivo, pagesize=letter, topMargin=5, bottomMargin=5)

            # Coleta os dados da tabela do GUI
            dados_tabela = [["Nome do Arquivo", "Hash Gerado (SHA-256)"]]  # Cabeçalhos da tabela
            for row in tree.get_children():
                nome_arquivo, hash_gerado = tree.item(row, 'values')
                dados_tabela.append([nome_arquivo, hash_gerado])

            # Criação da tabela
            tabela = Table(dados_tabela)

            # Estilos para a tabela
            estilo_tabela = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.gray),  # Cor de fundo para cabeçalho
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Cor do texto para cabeçalho
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alinhamento centralizado
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fonte do cabeçalho
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding no cabeçalho
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Cor de fundo para as linhas
                ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Grade de linhas
            ])
            tabela.setStyle(estilo_tabela)

            # Adiciona o cabeçalho com imagem
            img_path = obter_caminho_imagem('cabeçalho_pol_gov.jpg')
            if os.path.exists(img_path):
                imagem = Image(img_path, width=650, height=100)  # Ajuste o tamanho da imagem conforme necessário
            else:
                messagebox.showerror("Erro", f"Imagem '{img_path}' não encontrada.")
                return

            # Criação da mensagem com data e hora atuais
            data_atual = datetime.now().strftime("%d/%m/%Y")
            hora_atual = datetime.now().strftime("%H:%M:%S")
            mensagem = f'A tabela contendo o código hash referente a cada arquivo foi gerada na data "{data_atual}" às "{hora_atual}".'

            # Estilo para o parágrafo da mensagem
            estilo = getSampleStyleSheet()["Normal"]
            paragrafo_mensagem = Paragraph(mensagem, estilo)

            # Criação de elementos para o PDF (Cabeçalho + Mensagem + Tabela)
            elementos = [imagem, paragrafo_mensagem, tabela]

            # Geração do PDF
            pdf.build(elementos)
            messagebox.showinfo("Sucesso", f"PDF gerado em: {caminho_arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível gerar o PDF: {e}")


ctk.set_appearance_mode("dark")
janela = ctk.CTk()
janela.title("Leitor de Arquivos e Gerador de Hash")
janela.geometry("800x400")

# Botão para carregar arquivos
carregar_btn = ctk.CTkButton(janela, text="Carregar Arquivos", command=carregar_arquivos)
carregar_btn.pack(pady=10)

# Tabela para exibir os arquivos e seus hashes
tree = ttk.Treeview(janela, columns=("Arquivo", "Hash Gerado"), show="headings", height=10)
tree.heading("Arquivo", text="Nome do Arquivo")
tree.heading("Hash Gerado", text="Hash Gerado (SHA-256)")
tree.column("Arquivo", width=400)
tree.column("Hash Gerado", width=350)
tree.pack(pady=10)

# Botão para gerar PDF com a tabela de hashes
gerar_pdf_btn = ctk.CTkButton(janela, text="Gerar PDF com Hashes", command=gerar_pdf_tabela)
gerar_pdf_btn.pack(pady=10)

# Rodapé com o nome
footer_label = ctk.CTkLabel(janela, text="Desenvolvido por Nathanael Pereira Mesquita - IPC/PCCE", font=("Arial", 10))
footer_label.pack(side="bottom", anchor="e", padx=10, pady=10)  # 'anchor="e"' alinha à direita

janela.mainloop()
