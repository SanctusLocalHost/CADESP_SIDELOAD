import customtkinter as ctk
import requests
import pandas as pd
import os
import threading
import time
import webbrowser
from pathlib import Path
from tkinter import messagebox
from fpdf import FPDF
from datetime import datetime

# pip install customtkinter requests pandas openpyxl fpdf2--break-system-packages

class ConsultaEstruturada(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Cadastro de Contribuintes do ICMS do Estado")
        self.geometry("1050x950")
        self.configure(fg_color="#000000")
        
        self.dados_empresa = {}
        self.pasta_downloads = str(Path.home() / "Downloads")
        
        # Variáveis do Motor de Busca
        self.match_indices =[]
        self.current_match_idx = 0
        
        self.setup_ui()
        
        # Binds de Teclado
        self.entry_documento.bind("<Return>", lambda event: self.executar_fluxo())
        self.entry_documento.bind("<KP_Enter>", lambda event: self.executar_fluxo())
        
        # Binds para o Ctrl+F (Windows/Linux e Mac)
        self.bind("<Control-f>", self.abrir_busca)
        self.bind("<Control-F>", self.abrir_busca)
        self.bind("<Command-f>", self.abrir_busca)

    def setup_ui(self):
        # Título Interno
        self.lbl_titulo = ctk.CTkLabel(self, text="CONSULTA ESTRUTURADA DE DATABASE", 
                                       font=("Courier New", 26, "bold"), text_color="#00FF00")
        self.lbl_titulo.pack(side="top", pady=(30, 0))

        # Créditos e Link do Telegram
        self.lbl_creditos = ctk.CTkLabel(self, text="Development by @Sanctus_LocalHost", 
                                         font=("Courier New", 11, "underline"), text_color="#00AA00", cursor="hand2")
        self.lbl_creditos.pack(side="top", pady=(0, 20))
        self.lbl_creditos.bind("<Button-1>", lambda e: webbrowser.open("https://telegram.me/Sanctus_LocalHost"))

        # Frame Centralizador do Cabeçalho
        self.frame_comando = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_comando.pack(side="top", fill="x")

        self.frame_center = ctk.CTkFrame(self.frame_comando, fg_color="transparent")
        self.frame_center.pack(anchor="center")

        # 1. Dropdowns
        self.frame_dropdowns = ctk.CTkFrame(self.frame_center, fg_color="transparent")
        self.frame_dropdowns.pack(side="left", padx=8)

        self.tipo_busca_var = ctk.StringVar(value="CNPJ")
        self.tipo_busca_menu = ctk.CTkOptionMenu(
            self.frame_dropdowns, 
            values=["CNPJ", "INSCRIÇÃO ESTADUAL"],
            command=self.atualizar_apis,
            variable=self.tipo_busca_var,
            fg_color="#003300", button_color="#004400", text_color="#00FF00",
            font=("Courier New", 12, "bold"), dropdown_fg_color="#050505", width=160, height=32
        )
        self.tipo_busca_menu.pack(side="top", pady=(0, 4))

        self.api_selection = ctk.CTkOptionMenu(
            self.frame_dropdowns, 
            values=["BrasilAPI", "ReceitaWS", "CNPJ.ws", "MinhaReceita"],
            fg_color="#003300", button_color="#004400", text_color="#00FF00",
            font=("Courier New", 12), dropdown_fg_color="#050505", width=160, height=32
        )
        self.api_selection.pack(side="top")

        # 2. Entry Principal
        self.entry_documento = ctk.CTkEntry(self.frame_center, placeholder_text="CNPJ...", 
                                       width=280, height=45, font=("Courier New", 18),
                                       fg_color="#050505", border_color="#00FF00", border_width=2, text_color="#00FF00")
        self.entry_documento.pack(side="left", padx=15)

        # 3. Botões
        self.frame_botoes = ctk.CTkFrame(self.frame_center, fg_color="transparent")
        self.frame_botoes.pack(side="left", padx=8)

        self.btn_buscar = ctk.CTkButton(self.frame_botoes, text="EXECUTAR", 
                                        command=self.executar_fluxo, font=("Courier New", 14, "bold"),
                                        fg_color="#003300", hover_color="#005500", text_color="#00FF00", width=150, height=32)
        self.btn_buscar.pack(side="top", pady=(0, 4))

        self.btn_pdf = ctk.CTkButton(self.frame_botoes, text="EXPORTAR PDF", 
                                     command=self.processar_documento_final, font=("Courier New", 14, "bold"),
                                     state="disabled", fg_color="#1a1a1a", text_color="#444444", width=150, height=32)
        self.btn_pdf.pack(side="top")

        # Rodapé
        self.frame_rodape = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_rodape.pack(side="bottom", fill="x", pady=15, padx=20)

        self.lbl_pct = ctk.CTkLabel(self.frame_rodape, text="Status: Aguardando...", font=("Courier New", 12), text_color="#00FF00")
        self.lbl_pct.pack(side="top")
        
        self.bar = ctk.CTkProgressBar(self.frame_rodape, width=900, progress_color="#00FF00", fg_color="#002200")
        self.bar.set(0)
        self.bar.pack(side="top", pady=5)

        # --- BARRA DE BUSCA (CTRL+F) OCULTA POR PADRÃO ---
        self.frame_busca = ctk.CTkFrame(self, fg_color="#001500", height=40, corner_radius=0)
        
        self.entry_busca = ctk.CTkEntry(self.frame_busca, placeholder_text="Buscar no terminal...", 
                                        width=250, height=30, font=("Courier New", 12),
                                        fg_color="#050505", border_color="#00FF00", text_color="#00FF00")
        self.entry_busca.pack(side="left", padx=(10, 5), pady=5)
        self.entry_busca.bind("<KeyRelease>", self.realizar_busca)
        self.entry_busca.bind("<Return>", self.proximo_resultado)
        self.entry_busca.bind("<Escape>", self.fechar_busca)
        
        self.lbl_busca_count = ctk.CTkLabel(self.frame_busca, text="0/0", font=("Courier New", 12, "bold"), text_color="#00FF00")
        self.lbl_busca_count.pack(side="left", padx=10)
        
        self.btn_prev_busca = ctk.CTkButton(self.frame_busca, text="▲", width=30, height=30,
                                            fg_color="#003300", hover_color="#005500", text_color="#00FF00",
                                            command=self.resultado_anterior)
        self.btn_prev_busca.pack(side="left", padx=2)

        self.btn_next_busca = ctk.CTkButton(self.frame_busca, text="▼", width=30, height=30,
                                            fg_color="#003300", hover_color="#005500", text_color="#00FF00",
                                            command=self.proximo_resultado)
        self.btn_next_busca.pack(side="left", padx=2)
        
        self.btn_fechar_busca = ctk.CTkButton(self.frame_busca, text="X", width=30, height=30,
                                              fg_color="#330000", hover_color="#550000", text_color="#FF0000",
                                              command=self.fechar_busca)
        self.btn_fechar_busca.pack(side="right", padx=10)

        # Terminal
        self.txt_display = ctk.CTkTextbox(self, font=("Courier New", 12),
                                          fg_color="#050505", border_color="#00FF00", border_width=1, 
                                          text_color="#00FF00")
        self.txt_display.pack(side="top", pady=(15, 0), padx=30, expand=True, fill="both")

    # ==========================================
    # MOTOR DE BUSCA (CTRL + F)
    # ==========================================
    def abrir_busca(self, event=None):
        # Empacota a barra de busca logo acima do terminal
        self.frame_busca.pack(side="top", fill="x", padx=30, before=self.txt_display)
        self.entry_busca.focus()
        self.realizar_busca()

    def fechar_busca(self, event=None):
        self.frame_busca.pack_forget()
        self.txt_display.tag_remove("highlight", "1.0", "end")
        self.txt_display.tag_remove("current_highlight", "1.0", "end")
        self.entry_busca.delete(0, "end")
        self.lbl_busca_count.configure(text="0/0")

    def realizar_busca(self, event=None):
        # Ignora teclas de navegação para não refazer a busca à toa
        if event and event.keysym in ("Return", "Up", "Down", "Left", "Right", "Escape"):
            return
            
        self.txt_display.tag_remove("highlight", "1.0", "end")
        self.txt_display.tag_remove("current_highlight", "1.0", "end")
        self.match_indices =[]
        self.current_match_idx = 0
        
        query = self.entry_busca.get()
        if not query:
            self.lbl_busca_count.configure(text="0/0")
            return
            
        start_pos = "1.0"
        while True:
            # Acessa o widget Text interno do CTk para usar a função nativa de busca
            start_pos = self.txt_display._textbox.search(query, start_pos, stopindex="end", nocase=True)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(query)}c"
            self.txt_display.tag_add("highlight", start_pos, end_pos)
            self.match_indices.append((start_pos, end_pos))
            start_pos = end_pos
            
        # Cor dos resultados inativos (Fundo verde escuro, texto verde claro)
        self.txt_display.tag_config("highlight", background="#004400", foreground="#00FF00")
        
        if self.match_indices:
            self.destacar_resultado_atual()
        else:
            self.lbl_busca_count.configure(text="0/0")

    def destacar_resultado_atual(self):
        self.txt_display.tag_remove("current_highlight", "1.0", "end")
        if self.match_indices:
            start_pos, end_pos = self.match_indices[self.current_match_idx]
            self.txt_display.tag_add("current_highlight", start_pos, end_pos)
            # Cor do resultado ativo (Fundo verde neon, texto preto)
            self.txt_display.tag_config("current_highlight", background="#00FF00", foreground="#000000")
            self.txt_display.see(start_pos)
            self.lbl_busca_count.configure(text=f"{self.current_match_idx + 1}/{len(self.match_indices)}")

    def proximo_resultado(self, event=None):
        if self.match_indices:
            self.current_match_idx = (self.current_match_idx + 1) % len(self.match_indices)
            self.destacar_resultado_atual()

    def resultado_anterior(self, event=None):
        if self.match_indices:
            self.current_match_idx = (self.current_match_idx - 1) % len(self.match_indices)
            self.destacar_resultado_atual()

    # ==========================================
    # LÓGICA PRINCIPAL
    # ==========================================
    def atualizar_apis(self, escolha):
        if escolha == "CNPJ":
            self.api_selection.configure(values=["BrasilAPI", "ReceitaWS", "CNPJ.ws", "MinhaReceita"])
            self.api_selection.set("BrasilAPI")
            self.entry_documento.configure(placeholder_text="CNPJ...")
        elif escolha == "INSCRIÇÃO ESTADUAL":
            self.api_selection.configure(values=["BrasilAPI"])
            self.api_selection.set("BrasilAPI")
            self.entry_documento.configure(placeholder_text="Inscrição Estadual...")

    def executar_fluxo(self):
        documento = self.entry_documento.get().strip().replace(".", "").replace("/", "").replace("-", "")
        if not documento: return
        
        self.fechar_busca() # Fecha a barra de busca se estiver aberta
        self.btn_buscar.configure(state="disabled")
        self.btn_pdf.configure(state="disabled", fg_color="#1a1a1a", text_color="#444444")
        self.txt_display.delete("1.0", "end")
        
        self.bar.configure(mode="determinate")
        self.bar.set(0)
        
        threading.Thread(target=self.sequencia_logistica, args=(documento,), daemon=True).start()

    def sequencia_logistica(self, documento):
        mensagens =[
            ">>> ESTABLISHING SECURE TUNNEL TO DATABASE MIRROR...",
            ">>> PARSING RAW DATA STREAM FROM RFB/SEFAZ DATABASES...",
            ">>> INJECTING ANALYTICS MODULE...",
            ">>> CROSS-REFERENCING MATRICES...",
            ">>> COMPILING FINAL CADASTRO DATAPACK...",
            ">>> DECRYPTING PAYLOAD..."
        ]

        for i, msg in enumerate(mensagens):
            pct = int(((i + 1) / (len(mensagens) + 1)) * 100)
            self.lbl_pct.configure(text=f"Status: {pct}%")
            self.bar.set((i + 1) / (len(mensagens) + 1))
            
            # Efeito Typewriter (Máquina de Escrever)
            for char in msg:
                self.txt_display.insert("end", char)
                self.txt_display.see("end")
                time.sleep(0.001) 
            
            self.txt_display.insert("end", "\n")
            time.sleep(0.05) 

        self.lbl_pct.configure(text="Status: Aguardando resposta do servidor...")
        self.bar.configure(mode="indeterminate")
        self.bar.start()
        
        self.consultar_api(documento)

    def achatar_dicionario(self, d, parent_key='', sep='_'):
        items =[]
        if not isinstance(d, dict): return {parent_key: d}
            
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.achatar_dicionario(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                if not v: continue
                if all(isinstance(i, dict) for i in v):
                    for index, item in enumerate(v):
                        list_key = f"{new_key}_{index+1}"
                        items.extend(self.achatar_dicionario(item, list_key, sep=sep).items())
                else:
                    items.append((new_key, " | ".join(map(str, v))))
            else:
                items.append((new_key, str(v) if v is not None and str(v) != "" else "N/A"))
        return dict(items)

    def consultar_api(self, documento):
        escolha_api = self.api_selection.get()
        tipo_busca = self.tipo_busca_var.get()
        
        if tipo_busca == "CNPJ":
            urls = {
                "BrasilAPI": f"https://brasilapi.com.br/api/cnpj/v1/{documento}",
                "ReceitaWS": f"https://receitaws.com.br/v1/cnpj/{documento}",
                "CNPJ.ws": f"https://publica.cnpj.ws/cnpj/{documento}",
                "MinhaReceita": f"https://minhareceita.org/{documento}"
            }
            url = urls.get(escolha_api)
        else:
            urls = {"BrasilAPI": f"https://brasilapi.com.br/api/ie/v1/sp/{documento}"}
            url = urls.get(escolha_api)
        
        try:
            res = requests.get(url, timeout=15)
            self.bar.stop()
            self.bar.configure(mode="determinate")
            
            if res.status_code == 200:
                dados_brutos = res.json()
                dados_achatados = self.achatar_dicionario(dados_brutos)
                self.dados_empresa = {k: v for k, v in dados_achatados.items() if v not in["N/A", "None", "", "[]", "{}"]}
                
                self.classificar_perfil()
                self.mostrar_dados_terminal()
                
                self.lbl_pct.configure(text="Status: 100% - Concluído")
                self.bar.set(1.0)
                self.btn_pdf.configure(state="normal", fg_color="#00FF00", hover_color="#00CC00", text_color="#000000")
            elif res.status_code == 429:
                self.lbl_pct.configure(text="Status: Erro 429 (Muitas Requisições)")
                self.bar.set(0)
                self.txt_display.insert("end", f"\n[ ERRO 429 ] O servidor da API bloqueou temporariamente por excesso de consultas.\nPor favor, aguarde 1 minuto ou troque a API no menu acima.\n")
            else:
                self.lbl_pct.configure(text="Status: Erro na Consulta")
                self.bar.set(0)
                self.txt_display.insert("end", f"\n[ ERRO ] STATUS {res.status_code} - Documento inválido ou não encontrado.\n")
        except requests.exceptions.Timeout:
            self.bar.stop()
            self.bar.configure(mode="determinate")
            self.bar.set(0)
            self.lbl_pct.configure(text="Status: Tempo Esgotado")
            self.txt_display.insert("end", f"\n[ FALHA ] Tempo de resposta esgotado (Timeout). Tente novamente.\n")
        except Exception as e:
            self.bar.stop()
            self.bar.configure(mode="determinate")
            self.bar.set(0)
            self.lbl_pct.configure(text="Status: Falha Crítica")
            self.txt_display.insert("end", f"\n[ FALHA ] {str(e)}\n")
        finally:
            self.btn_buscar.configure(state="normal")

    def classificar_perfil(self):
        d = self.dados_empresa
        nome = str(d.get('razao_social', d.get('nome', d.get('estabelecimento_nome_fantasia', '')))).upper()
        conteudo = str(d).upper()
        
        keywords_ind =["FABRICACAO", "FABRICA", "INDUSTRIA", "INDUSTRIAL", "PRODUCAO", "USINA"]
        keywords_com =["DISTRIBUIDOR", "COMERCIO", "VAREJISTA", "ATACADISTA", "REVENDA", "LOJA"]

        e_ind = any(k in nome or k in conteudo for k in keywords_ind)
        e_com = any(k in nome or k in conteudo for k in keywords_com)

        if e_ind and e_com: p = "INDÚSTRIA E COMÉRCIO"
        elif e_ind: p = "INDÚSTRIA"
        elif e_com: p = "COMÉRCIO"
        else: p = "OUTROS"
        self.dados_empresa['PERFIL_FINAL'] = p

    def mostrar_dados_terminal(self):
        d = self.dados_empresa
        self.txt_display.insert("end", "\n" + "="*70 + "\n")
        self.txt_display.insert("end", f" CLASSIFICAÇÃO IDENTIFICADA: {d.get('PERFIL_FINAL')}\n")
        self.txt_display.insert("end", "="*70 + "\n\n")

        for k, v in d.items():
            self.txt_display.insert("end", f"{k.upper():<45}: {v}\n")
        
        self.txt_display.insert("end", "\n" + "-"*70 + "\n[ PRONTO PARA EXPORTAR ]\n")
        self.txt_display.see("end")

    def processar_documento_final(self):
        d = self.dados_empresa
        doc_num = "".join(filter(str.isdigit, str(d.get('cnpj', d.get('inscricao_estadual', 'DOC')))))
        path_xlsx = os.path.join(self.pasta_downloads, f"TEMP_{doc_num}.xlsx")
        path_pdf = os.path.join(self.pasta_downloads, f"CADESP_{doc_num}.pdf")

        # 1. EXCEL
        df_list =[{"CAMPO": k.upper(), "VALOR": v} for k, v in d.items()]
        pd.DataFrame(df_list).to_excel(path_xlsx, index=False)

        # 2. PDF
        pdf = FPDF('P', 'mm', 'A4')
        pdf.add_page()
        
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(95, 10, "Consulta Cadastral", border=0, align='L')
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(95, 10, "Cadastro de Contribuintes de ICMS - Cadesp", border=0, align='R', ln=True)
        pdf.set_draw_color(100, 100, 100)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        grupos = {
            "Empresa - Geral": {},
            "Estabelecimento e Contato": {},
            "Tributário e Atividades": {},
            "Participantes (Sócios)": {},
            "Outras Informações": {}
        }

        for k, v in d.items():
            kl = k.lower()
            if any(x in kl for x in['socio', 'qsa', 'participante', 'qualificacao']):
                grupos["Participantes (Sócios)"][k] = v
            elif any(x in kl for x in['cnae', 'atividade', 'tribut', 'simples', 'simei', 'natureza_juridica']):
                grupos["Tributário e Atividades"][k] = v
            elif any(x in kl for x in['cep', 'logradouro', 'bairro', 'municipio', 'cidade', 'uf', 'estado', 'telefone', 'email', 'ddd', 'fax', 'numero', 'complemento']):
                grupos["Estabelecimento e Contato"][k] = v
            elif any(x in kl for x in['cnpj', 'razao', 'nome', 'fantasia', 'porte', 'capital', 'situacao', 'abertura', 'inicio', 'motivo', 'ie', 'inscricao', 'perfil']):
                grupos["Empresa - Geral"][k] = v
            else:
                grupos["Outras Informações"][k] = v

        for nome_grupo, dados_grupo in grupos.items():
            if not dados_grupo: continue

            pdf.ln(4)
            pdf.set_font("Arial", 'B', 10)
            pdf.set_fill_color(230, 230, 230)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(190, 8, nome_grupo, border=1, fill=True, align='C', ln=True)

            pdf.set_font("Arial", size=8)
            fill = False
            for k, v in dados_grupo.items():
                if pdf.get_y() > 270:
                    pdf.add_page()
                
                pdf.set_fill_color(248, 248, 248) if fill else pdf.set_fill_color(255, 255, 255)
                
                x = pdf.get_x()
                y = pdf.get_y()
                
                pdf.set_font("Arial", 'B', 7)
                pdf.multi_cell(75, 6, f" {k.upper()}", border=1, fill=True)
                y_fim_campo = pdf.get_y()
                
                pdf.set_xy(x + 75, y)
                pdf.set_font("Arial", '', 8)
                pdf.multi_cell(115, 6, f" {v}", border=1, fill=True)
                y_fim_valor = pdf.get_y()
                
                pdf.set_y(max(y_fim_campo, y_fim_valor))
                fill = not fill 

        pdf.ln(10)
        pdf.set_font("Arial", 'I', 7)
        pdf.cell(0, 5, f"Relatório gerado automaticamente em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", align='C')

        if os.path.exists(path_xlsx): os.remove(path_xlsx)
        
        try:
            pdf.output(path_pdf)
            messagebox.showinfo("Sucesso", f"PDF Exportado para Downloads!\nArquivo: CADESP_{doc_num}.pdf")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar PDF: {e}")

if __name__ == "__main__":
    app = ConsultaEstruturada()
    app.mainloop()