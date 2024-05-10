import tkinter as tk
from tkinter import filedialog
from googletrans import Translator
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import fitz

def exibir_mensagem(mensagem):
    label_status["text"] = mensagem

def mostrar_mensagem_aguardando():
    mensagem["text"] = "Aguarde, traduzindo o texto..."

def remover_mensagem_aguardando():
    mensagem["text"] = ""

def extrair_texto_pdf(arquivo_pdf):
    texto = ""
    try:
        with fitz.open(arquivo_pdf) as pdf_doc:
            num_paginas = pdf_doc.page_count
            for pagina_num in range(num_paginas):
                pagina = pdf_doc[pagina_num]
                texto += pagina.get_text()
        return texto
    except Exception as e:
        return f"Erro ao extrair texto do PDF: {str(e)}"

def criar_arquivo_txt(texto, nome_arquivo):
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as txt_file:
            txt_file.write(texto)
        return True
    except Exception as e:
        print(f"Erro ao criar arquivo TXT: {str(e)}")
        return False

def traduzir_e_criar_arquivo_traduzido(arquivo_pdf):
    mostrar_mensagem_aguardando()  # Exibe a mensagem de aguardo
    texto = extrair_texto_pdf(arquivo_pdf)
    if texto:
        trechos = dividir_em_trechos(texto)
        trechos_traduzidos = traduzir_trechos(trechos)
        nome_arquivo_txt = arquivo_pdf.replace('.pdf', '_traduzido.txt')
        if criar_arquivo_txt('\n'.join(trechos_traduzidos), nome_arquivo_txt):
            label_status["text"] = f"Texto traduzido com sucesso. Arquivo TXT criado: {nome_arquivo_txt}"
            converter_txt_para_pdf(nome_arquivo_txt)
        else:
            label_status["text"] = "Erro ao criar o arquivo TXT."
    else:
        label_status["text"] = "Erro ao extrair texto do PDF."
    remover_mensagem_aguardando()  # Remove a mensagem de aguardo

def dividir_em_trechos(texto, tamanho_trecho=4999):
    return [texto[i:i+tamanho_trecho] for i in range(0, len(texto), tamanho_trecho)]

def traduzir_trechos(trechos):
    translator = Translator()
    trechos_traduzidos = []

    for trecho in trechos:
        try:
            traducao = translator.translate(trecho, dest='pt').text
            trechos_traduzidos.append(traducao)
        except Translator.ServiceError as e:
            print(f"Erro ao traduzir trecho: {str(e)}")
            trechos_traduzidos.append("Erro na tradução")

    return trechos_traduzidos

def converter_txt_para_pdf(arquivo_txt):
    nome_arquivo_pdf = arquivo_txt.replace('_traduzido.txt', '_traduzido.pdf')
    pdf = canvas.Canvas(nome_arquivo_pdf, pagesize=letter)

    with open(arquivo_txt, 'r', encoding='utf-8') as txt_file:
        trechos_traduzidos = txt_file.readlines()
        y = 750  # Posição inicial na página
        for trecho_traduzido in trechos_traduzidos:
            # Centralizando o texto horizontalmente
            text_width = pdf.stringWidth(trecho_traduzido.strip(), "Helvetica", 12)
            x = (letter[0] - text_width) / 2
            pdf.drawString(x, y, trecho_traduzido.strip())
            y -= 20  # Espaço entre linhas

            # Verificando se é necessário adicionar uma nova página
            if y <= 50:  # Se a próxima linha ultrapassar a margem inferior
                pdf.showPage()  # Adiciona uma nova página
                y = 750  # Reseta a posição y para o topo da nova página

    pdf.save()
    label_status["text"] += f"\nArquivo PDF criado: {nome_arquivo_pdf}"

def abrir_selecionar_pdf():
    arquivo_pdf = filedialog.askopenfilename(
        title="Selecione um arquivo PDF",
        filetypes=[("Arquivos PDF", "*.pdf")],
    )
    if arquivo_pdf:
        traduzir_e_criar_arquivo_traduzido(arquivo_pdf)
        exibir_mensagem("Arquivo enviado com sucesso!")

# Interface Gráfica
root = tk.Tk()
root.title("Extrair Texto de PDF e Traduzir")

frame_pdf = tk.Frame(root, padx=10, pady=10)
frame_pdf.pack(padx=20, pady=20)

btn_selecionar_pdf = tk.Button(frame_pdf, text="Selecionar PDF", command=abrir_selecionar_pdf)
btn_selecionar_pdf.pack()

label_status = tk.Label(frame_pdf, text="")
label_status.pack()

mensagem = tk.Label(frame_pdf, text="")
mensagem.pack()

root.mainloop()
