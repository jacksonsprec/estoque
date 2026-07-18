import os
from datetime import datetime
from tkinter import filedialog, messagebox, simpledialog, ttk
import tkinter as tk

from modules.config import carregar_configuracao, obter_senha_remocao, salvar_configuracao
from modules.persistence import carregar_dados, carregar_lixeira, carregar_tema, salvar_dados, salvar_lixeira, salvar_tema
from modules.validations import dias_ate_validade, validar_quantidade, validar_validade
from modules.views import ConsultaView, EntradaView, LogView, RetiradaView, ToolbarView

ICON_FILE = "app_icon.ico"
DATE_TIME_FORMAT = "%d/%m/%Y %H:%M:%S"
DATE_ONLY_FORMAT = "%d/%m/%Y"


class EstoqueApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gerenciador de Estoque")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        self.root.option_add("*Font", "TkDefaultFont 10")
        if os.path.exists(ICON_FILE):
            try:
                self.root.iconbitmap(default=ICON_FILE)
            except tk.TclError:
                pass
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.tema_atual = self.carregar_tema()
        self.widgets_tema = []

        self.configuracao = self.carregar_configuracao()
        self.estoque = self.carregar_dados()
        self.lixeira = self.carregar_lixeira()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.frame_entrada = ttk.Frame(self.notebook)
        self.frame_retirada = ttk.Frame(self.notebook)
        self.frame_consulta = ttk.Frame(self.notebook)
        self.frame_log = ttk.Frame(self.notebook)

        self.notebook.add(self.frame_entrada, text="01 - Entrada")
        self.notebook.add(self.frame_retirada, text="02 - Retirada")
        self.notebook.add(self.frame_consulta, text="03 - Estoque")
        self.notebook.add(self.frame_log, text="04 - Log")

        self.toolbar_view = ToolbarView(self.root, self)
        self.entrada_view = EntradaView(self.frame_entrada, self)
        self.retirada_view = RetiradaView(self.frame_retirada, self)
        self.consulta_view = ConsultaView(self.frame_consulta, self)
        self.log_view = LogView(self.frame_log, self)
        self.aplicar_tema(self.tema_atual)
        self.atualizar_tela_consulta()
        self.exibir_alerta_inicio_validade()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def carregar_configuracao(self):
        return carregar_configuracao()

    def salvar_configuracao(self):
        salvar_configuracao(self.configuracao)

    def obter_senha_remocao(self):
        return obter_senha_remocao(self.configuracao)

    def carregar_tema(self):
        return carregar_tema()

    def salvar_tema(self, tema):
        salvar_tema(tema)

    def alternar_tema(self):
        novo_tema = "escuro" if self.tema_atual == "claro" else "claro"
        self.aplicar_tema(novo_tema)
        self.salvar_tema(novo_tema)

    def aplicar_tema(self, tema):
        self.tema_atual = tema

        if tema == "escuro":
            bg = "#1f1f1f"
            fg = "#f5f5f5"
            fg_muted = "#d0d0d0"
            campo = "#2d2d2d"
            borda = "#555555"
            destaque = "#2f6fed"
            linha = "#333333"
            texto = "#f0f0f0"
            texto_muted = "#b7b7b7"
            botao_bg = "#3a3a3a"
            botao_fg = "#ffffff"
            hover = "#4c4c4c"
            header = "#2a2a2a"
            tree_bg = "#252525"
        else:
            bg = "#f7f7f7"
            fg = "#1a1a1a"
            fg_muted = "#444444"
            campo = "#ffffff"
            borda = "#cfcfcf"
            destaque = "#1f6feb"
            linha = "#e3e3e3"
            texto = "#111111"
            texto_muted = "#555555"
            botao_bg = "#efefef"
            botao_fg = "#111111"
            hover = "#dfe8f8"
            header = "#e9eef6"
            tree_bg = "#ffffff"

        self.root.configure(bg=bg)
        self.toolbar.configure(style="TFrame")
        self.notebook.configure(style="TNotebook")

        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("TButton", background=botao_bg, foreground=botao_fg, borderwidth=1, padding=(12, 7), relief="flat")
        self.style.map(
            "TButton",
            background=[("active", hover), ("pressed", hover), ("!disabled", botao_bg)],
            foreground=[("active", botao_fg), ("disabled", fg_muted)],
        )

        self.style.configure("TNotebook", background=bg, bordercolor=borda, padding=(0, 0))
        self.style.configure("TNotebook.Tab", background=bg, foreground=fg, bordercolor=borda, padding=(12, 6))
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", linha), ("active", hover)],
            foreground=[("selected", fg), ("active", fg)],
        )

        self.style.configure("TCombobox", fieldbackground=campo, background=campo, foreground=fg, bordercolor=borda, padding=(6, 4))
        self.style.map("TCombobox", background=[("active", hover), ("!disabled", campo)], foreground=[("disabled", fg_muted)])

        self.style.configure("TSpinbox", fieldbackground=campo, background=campo, foreground=fg, bordercolor=borda, padding=(6, 4))
        self.style.map("TSpinbox", background=[("active", hover), ("!disabled", campo)], foreground=[("disabled", fg_muted)])

        self.style.configure("TEntry", fieldbackground=campo, foreground=fg, bordercolor=borda, padding=(6, 4))
        self.style.configure("Treeview", background=tree_bg, foreground=texto, fieldbackground=tree_bg, bordercolor=borda)
        self.style.configure("Treeview.Heading", background=header, foreground=fg, bordercolor=borda, relief="flat")
        self.style.map("Treeview.Heading", background=[("active", hover)])

        for widget in self.widgets_tema:
            try:
                if isinstance(widget, tk.Entry):
                    widget.configure(background=campo, foreground=texto, relief="flat")
                    try:
                        widget.configure(insertbackground=texto)
                    except tk.TclError:
                        pass
                elif isinstance(widget, tk.Text):
                    widget.configure(background=campo, foreground=texto)
                    try:
                        widget.configure(insertbackground=texto)
                    except tk.TclError:
                        pass
                elif isinstance(widget, tk.Spinbox):
                    widget.configure(background=campo, foreground=texto, relief="flat")
                elif isinstance(widget, ttk.Combobox):
                    widget.configure(style="TCombobox")
                elif isinstance(widget, ttk.Frame):
                    widget.configure(style="TFrame")
                elif isinstance(widget, tk.Label):
                    widget.configure(background=bg, foreground=fg)
                elif isinstance(widget, ttk.Button):
                    widget.configure(style="TButton")
                elif isinstance(widget, ttk.Treeview):
                    widget.configure(style="Treeview")
            except tk.TclError:
                continue

        self.botao_tema.configure(text=f"Tema: {'Escuro' if tema == 'escuro' else 'Claro'}")

        self.tree_estoque.tag_configure("selected", background=destaque, foreground=texto)

    def carregar_dados(self):
        return carregar_dados()

    def carregar_lixeira(self):
        return carregar_lixeira()

    def salvar_dados(self):
        salvar_dados(self.estoque, self.configuracao)

    def salvar_lixeira(self):
        salvar_lixeira(self.lixeira, self.configuracao)

    def gerar_chave_material(self, nome, validade):
        nome = nome.strip()
        validade = validade.strip()

        if not nome:
            return nome

        if validade:
            chave_base = f"{nome} | {validade}"
        else:
            chave_base = nome

        if chave_base in self.estoque["itens"]:
            return chave_base

        contador = 1
        chave = chave_base
        while chave in self.estoque["itens"]:
            chave = f"{chave_base} ({contador})"
            contador += 1
        return chave

    def validar_quantidade(self, quantidade):
        return validar_quantidade(quantidade)

    def validar_validade(self, validade):
        return validar_validade(validade)

    def dias_ate_validade(self, validade):
        return dias_ate_validade(validade)

    def atualizar_status(self, mensagem):
        self.status_var.set(mensagem)

    def registrar_movimentacao(self, chave_material, nome, tipo, quantidade, motivo):
        agora = datetime.now()
        data = agora.strftime(DATE_ONLY_FORMAT)
        hora = agora.strftime("%H:%M:%S")

        movimento = {
            "chave_material": chave_material,
            "tipo": tipo,
            "nome": nome,
            "quantidade": quantidade,
            "motivo": motivo,
            "data": data,
            "hora": hora,
        }

        self.estoque["log_global"].append(movimento)

        if chave_material in self.estoque["itens"]:
            self.estoque["itens"][chave_material]["log"].append(movimento)

        self.salvar_dados()

    def criar_tela_entrada(self):
        EntradaView(self.frame_entrada, self)

    def criar_tela_retirada(self):
        RetiradaView(self.frame_retirada, self)

    def criar_tela_consulta(self):
        ConsultaView(self.frame_consulta, self)

    def selecionar_material_existente(self, event=None):
        valor = self.entrada_material_existente.get().strip()
        if not valor:
            return

        item = self.estoque["itens"].get(valor)
        if item is None:
            for chave, material in self.estoque["itens"].items():
                if material.get("nome") == valor:
                    item = material
                    break

        if item is None:
            return

        nome = item.get("nome", valor)
        self.entrada_nome.delete(0, tk.END)
        self.entrada_nome.insert(0, nome)
        self.autopreencher_descricao()

    def autopreencher_descricao(self, event=None):
        nome = self.entrada_nome.get().strip()
        if not nome:
            return

        item = None
        chave_selecionado = self.entrada_material_existente.get().strip()
        if chave_selecionado in self.estoque["itens"]:
            item = self.estoque["itens"].get(chave_selecionado)
        else:
            for chave, material in self.estoque["itens"].items():
                if material.get("nome") == nome:
                    item = material
                    break

        if item:
            self.entrada_descricao.delete(0, tk.END)
            self.entrada_descricao.insert(0, item["descricao"])
            self.entrada_validade.delete(0, tk.END)
            self.entrada_validade.insert(0, item["validade"])

    def formatar_validade(self, event=None):
        texto = self.entrada_validade.get().strip()
        numeros = "".join(caracter for caracter in texto if caracter.isdigit())

        if len(numeros) <= 2:
            data_formatada = numeros
        elif len(numeros) <= 4:
            data_formatada = f"{numeros[:2]}/{numeros[2:]}"
        else:
            data_formatada = f"{numeros[:2]}/{numeros[2:4]}/{numeros[4:8]}"

        self.entrada_validade.delete(0, tk.END)
        self.entrada_validade.insert(0, data_formatada[:10])

    def registrar_entrada(self):
        nome = self.entrada_nome.get().strip()
        descricao = self.entrada_descricao.get().strip()
        quantidade_texto = self.entrada_quantidade.get().strip()
        validade = self.entrada_validade.get().strip()
        motivo = self.entrada_motivo.get().strip()

        if not nome:
            messagebox.showwarning("Campo obrigatório", "Informe o nome do material antes de registrar a entrada.")
            return

        try:
            quantidade = self.validar_quantidade(quantidade_texto or 1)
            validade = self.validar_validade(validade)
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))
            return

        agora = datetime.now()
        chegada = agora.strftime(DATE_TIME_FORMAT)

        chave_material = self.gerar_chave_material(nome, validade)

        if chave_material in self.estoque["itens"]:
            self.estoque["itens"][chave_material]["quantidade"] += quantidade
            if descricao:
                self.estoque["itens"][chave_material]["descricao"] = descricao
            if validade:
                self.estoque["itens"][chave_material]["validade"] = validade
            self.estoque["itens"][chave_material]["nome"] = nome
        else:
            self.estoque["itens"][chave_material] = {
                "nome": nome,
                "descricao": descricao or "",
                "quantidade": quantidade,
                "validade": validade or "",
                "chegada": chegada,
                "log": [],
            }

        self.registrar_movimentacao(chave_material, nome, "entrada", quantidade, motivo or "Sem motivo informado")
        self.atualizar_tela_consulta()
        self.limpar_campos_entrada()
        self.atualizar_status(f"Entrada registrada para {nome}.")
        messagebox.showinfo("Sucesso", f"Entrada registrada para {nome}.")

    def registrar_retirada(self):
        chave_material = self.retirada_material.get().strip()
        quantidade_texto = self.retirada_quantidade.get().strip()
        motivo = self.retirada_motivo.get().strip()

        if not chave_material:
            messagebox.showwarning("Campo obrigatório", "Selecione o material antes de registrar a retirada.")
            return

        try:
            quantidade = self.validar_quantidade(quantidade_texto or 1)
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))
            return

        if chave_material not in self.estoque["itens"]:
            messagebox.showerror("Erro", "Material não encontrado no estoque.")
            return

        item = self.estoque["itens"][chave_material]
        nome = item.get("nome", chave_material)
        if quantidade > item["quantidade"]:
            messagebox.showerror("Erro", "Quantidade indisponível para retirada.")
            return

        item["quantidade"] -= quantidade
        self.registrar_movimentacao(chave_material, nome, "retirada", quantidade, motivo or "Sem motivo informado")
        self.atualizar_tela_consulta()
        self.limpar_campos_retirada()
        self.atualizar_status(f"Retirada registrada para {nome}.")
        messagebox.showinfo("Sucesso", f"Retirada registrada para {nome}.")

    def limpar_campos_entrada(self):
        self.entrada_nome.delete(0, tk.END)
        self.entrada_descricao.delete(0, tk.END)
        self.entrada_quantidade.delete(0, tk.END)
        self.entrada_quantidade.insert(0, "1")
        self.entrada_validade.delete(0, tk.END)
        self.entrada_motivo.delete(0, tk.END)

    def limpar_campos_retirada(self):
        self.retirada_quantidade.delete(0, tk.END)
        self.retirada_quantidade.insert(0, "1")
        self.retirada_motivo.delete(0, tk.END)

    def dias_ate_validade(self, validade):
        if not validade:
            return None

        try:
            data_validade = datetime.strptime(validade, DATE_ONLY_FORMAT).date()
        except ValueError:
            return None

        return (data_validade - datetime.now().date()).days

    def obter_alertas_validade(self):
        alertas = {
            "15dias": [],
            "10dias": [],
            "5dias": [],
            "vencidos": [],
        }

        for chave, item in self.estoque["itens"].items():
            dias = self.dias_ate_validade(item.get("validade", ""))
            if dias is None:
                continue
            nome = item.get("nome", chave)
            validade = item.get("validade", "")
            if dias < 0:
                alertas["vencidos"].append(f"{nome} — validade {validade} — vencido há {abs(dias)} dia(s)")
            elif dias <= 5:
                alertas["5dias"].append(f"{nome} — validade {validade} — falta(m) {dias} dia(s)")
            elif dias <= 10:
                alertas["10dias"].append(f"{nome} — validade {validade} — falta(m) {dias} dia(s)")
            elif dias <= 15:
                alertas["15dias"].append(f"{nome} — validade {validade} — falta(m) {dias} dia(s)")

        return alertas

    def exibir_alerta_inicio_validade(self):
        alertas = self.obter_alertas_validade()
        total_alertas = sum(len(v) for v in alertas.values())
        if total_alertas == 0:
            return

        linhas = []
        if alertas["vencidos"]:
            linhas.append("Materiais vencidos:")
            for item in alertas["vencidos"]:
                linhas.append(f"- {item}")

        if alertas["5dias"]:
            linhas.append("\nVencendo em até 5 dias:")
            for item in alertas["5dias"]:
                linhas.append(f"- {item}")

        if alertas["10dias"]:
            linhas.append("\nVencendo em até 10 dias:")
            for item in alertas["10dias"]:
                linhas.append(f"- {item}")

        if alertas["15dias"]:
            linhas.append("\nVencendo em até 15 dias:")
            for item in alertas["15dias"]:
                linhas.append(f"- {item}")

        messagebox.showwarning(
            "Alerta de validade",
            "Há itens com validade próxima ou vencida:\n\n" + "\n".join(linhas),
        )

    def filtrar_estoque(self, event=None):
        self.atualizar_tela_consulta()

    def atualizar_tela_consulta(self):
        self.tree_estoque.delete(*self.tree_estoque.get_children())
        termo_busca = self.busca_material.get().strip().lower() if hasattr(self, "busca_material") else ""
        filtro_validade = self.filtro_validade.get() if hasattr(self, "filtro_validade") else "Todos"

        materiais = []
        for chave, item in self.estoque["itens"].items():
            nome = item.get("nome", chave)
            validade = item.get("validade", "")
            dias = self.dias_ate_validade(validade)

            if termo_busca and termo_busca not in nome.lower() and termo_busca not in chave.lower():
                continue

            if filtro_validade == "Vencendo em até 30 dias":
                if dias is None or dias < 0 or dias > 30:
                    continue
            elif filtro_validade == "Vencidos":
                if dias is None or dias >= 0:
                    continue
            elif filtro_validade == "Sem validade":
                if validade:
                    continue

            materiais.append((chave, item, nome))

        materiais.sort(key=lambda item: (-item[1]["quantidade"], item[2], item[0]))

        for chave, item, nome in materiais:
            self.tree_estoque.insert(
                "",
                "end",
                iid=chave,
                values=(nome, item["quantidade"], item["validade"], chave),
            )

        opcoes = list(self.estoque["itens"].keys())
        self.retirada_material["values"] = opcoes
        self.entrada_material_existente["values"] = opcoes
        if opcoes:
            self.retirada_material.set(opcoes[0])
            self.entrada_material_existente.set(opcoes[0])

        total_itens = sum(item["quantidade"] for item in self.estoque["itens"].values())
        total_sem_validade = sum(1 for item in self.estoque["itens"].values() if not item.get("validade"))
        total_vencendo = sum(
            1
            for item in self.estoque["itens"].values()
            if self.dias_ate_validade(item.get("validade", "")) is not None
            and 0 <= self.dias_ate_validade(item.get("validade", "")) <= 30
        )
        total_vencidos = sum(
            1
            for item in self.estoque["itens"].values()
            if self.dias_ate_validade(item.get("validade", "")) is not None
            and self.dias_ate_validade(item.get("validade", "")) < 0
        )

        self.dashboard_text.configure(state="normal")
        self.dashboard_text.delete("1.0", tk.END)
        self.dashboard_text.insert(
            "1.0",
            f"Materiais cadastrados: {len(self.estoque['itens'])}\n"
            f"Quantidade total no estoque: {total_itens}\n"
            f"Itens sem validade: {total_sem_validade}\n"
            f"Vencendo em até 30 dias: {total_vencendo}\n"
            f"Vencidos: {total_vencidos}"
        )
        self.dashboard_text.configure(state="disabled")

        alertas = self.obter_alertas_validade()

        self.alerta_validade.configure(state="normal")
        self.alerta_validade.delete("1.0", tk.END)

        if not any(alertas.values()):
            self.alerta_validade.insert("1.0", "Nenhum alerta de validade no momento.")
            self.alerta_validade.configure(state="disabled")
            self.atualizar_status(f"{len(self.estoque['itens'])} materiais cadastrados · estoque total: {total_itens}")
            return

        if alertas["vencidos"]:
            self.alerta_validade.insert("1.0", "VENCIDOS:\n", "titulo_vencido")
            for item in alertas["vencidos"]:
                self.alerta_validade.insert("end", f"{item}\n", "vencido")

        if alertas["5dias"]:
            self.alerta_validade.insert("end", "\nPRÓXIMOS 5 DIAS:\n", "titulo_5")
            for item in alertas["5dias"]:
                self.alerta_validade.insert("end", f"{item}\n", "proximo_5")

        if alertas["10dias"]:
            self.alerta_validade.insert("end", "\nPRÓXIMOS 10 DIAS:\n", "titulo_10")
            for item in alertas["10dias"]:
                self.alerta_validade.insert("end", f"{item}\n", "proximo_10")

        if alertas["15dias"]:
            self.alerta_validade.insert("end", "\nPRÓXIMOS 15 DIAS:\n", "titulo_15")
            for item in alertas["15dias"]:
                self.alerta_validade.insert("end", f"{item}\n", "proximo_15")

        self.alerta_validade.configure(state="disabled")

        self.atualizar_status(f"{len(self.estoque['itens'])} materiais cadastrados · estoque total: {total_itens}")

    def exportar_relatorio_pdf(self):
        arquivo = filedialog.asksaveasfilename(
            title="Salvar relatório em PDF",
            defaultextension=".pdf",
            filetypes=[("Arquivo PDF", "*.pdf")],
        )
        if not arquivo:
            return

        try:
            from modules.reporting import exportar_relatorio_pdf as exportar_relatorio_pdf_func
        except ModuleNotFoundError as exc:
            if exc.name == "reportlab":
                messagebox.showerror(
                    "Dependência ausente",
                    "Para exportar relatórios em PDF, a biblioteca 'reportlab' precisa estar instalada.\n\n"
                    "No terminal, execute:\n"
                    "py -m pip install reportlab\n\n"
                    "Depois tente novamente.",
                )
                return
            raise

        exportar_relatorio_pdf_func(self.estoque, arquivo)
        self.atualizar_status(f"Relatório exportado para {arquivo}.")
        messagebox.showinfo("Sucesso", f"Relatório exportado com sucesso em:\n{arquivo}")

    def mostrar_log_do_material(self, event):
        selecionado = self.tree_estoque.selection()
        if not selecionado:
            return

        valores = self.tree_estoque.item(selecionado[0], "values")
        chave_material = valores[3]
        item = self.estoque["itens"].get(chave_material)

        if not item:
            return

        nome = item.get("nome", chave_material)
        self.material_selecionado_chave = chave_material
        self.consulta_material_var.set(f"{nome} ({item['validade']})" if item.get("validade") else nome)

        self.info_material.configure(state="normal")
        self.info_material.delete("1.0", tk.END)
        self.info_material.insert(
            "1.0",
            f"Material: {nome}\n"
            f"Descrição: {item['descricao']}\n"
            f"Quantidade atual: {item['quantidade']}\n"
            f"Validade: {item['validade']}\n"
            f"Data e hora de chegada: {item['chegada']}"
        )
        self.info_material.configure(state="disabled")

        self.log_material.configure(state="normal")
        self.log_material.delete("1.0", tk.END)
        texto = []
        for movimento in item["log"]:
            texto.append(
                f"[{movimento['data']} {movimento['hora']}] {movimento['tipo'].upper()} - "
                f"Quantidade: {movimento['quantidade']} | Motivo: {movimento['motivo']}"
            )

        if not texto:
            self.log_material.insert("1.0", "Nenhuma movimentação registrada para este material.")
        else:
            self.log_material.insert("1.0", "\n".join(texto))
        self.log_material.configure(state="disabled")

    def entrada_rapida_consulta(self):
        chave_material = getattr(self, "material_selecionado_chave", "")
        nome = self.consulta_material_var.get().strip()
        if chave_material == "" or nome == "Nenhum material selecionado" or not nome:
            messagebox.showwarning("Seleção obrigatória", "Selecione um material na tabela antes de movimentar.")
            return

        quantidade_texto = self.consulta_quantidade.get().strip()
        motivo = self.consulta_motivo.get().strip()

        try:
            quantidade = self.validar_quantidade(quantidade_texto or 1)
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))
            return

        item = self.estoque["itens"].get(chave_material)
        if not item:
            messagebox.showerror("Erro", "Material não encontrado no estoque.")
            return

        item["quantidade"] += quantidade
        self.registrar_movimentacao(chave_material, item.get("nome", chave_material), "entrada", quantidade, motivo or "Sem motivo informado")
        self.atualizar_tela_consulta()
        self.mostrar_log_do_material(None)
        self.consulta_motivo.delete(0, tk.END)
        self.consulta_quantidade.delete(0, tk.END)
        self.consulta_quantidade.insert(0, "1")
        self.atualizar_status(f"Entrada rápida registrada para {nome}.")
        messagebox.showinfo("Sucesso", f"Entrada rápida registrada para {nome}.")

    def retirada_rapida_consulta(self):
        chave_material = getattr(self, "material_selecionado_chave", "")
        nome = self.consulta_material_var.get().strip()
        if chave_material == "" or nome == "Nenhum material selecionado" or not nome:
            messagebox.showwarning("Seleção obrigatória", "Selecione um material na tabela antes de movimentar.")
            return

        quantidade_texto = self.consulta_quantidade.get().strip()
        motivo = self.consulta_motivo.get().strip()

        try:
            quantidade = self.validar_quantidade(quantidade_texto or 1)
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))
            return

        item = self.estoque["itens"].get(chave_material)
        if not item:
            messagebox.showerror("Erro", "Material não encontrado no estoque.")
            return
        if quantidade > item["quantidade"]:
            messagebox.showerror("Erro", "Quantidade indisponível para retirada.")
            return

        item["quantidade"] -= quantidade
        self.registrar_movimentacao(chave_material, item.get("nome", chave_material), "retirada", quantidade, motivo or "Sem motivo informado")
        self.atualizar_tela_consulta()
        self.mostrar_log_do_material(None)
        self.consulta_motivo.delete(0, tk.END)
        self.consulta_quantidade.delete(0, tk.END)
        self.consulta_quantidade.insert(0, "1")
        self.atualizar_status(f"Retirada rápida registrada para {nome}.")
        messagebox.showinfo("Sucesso", f"Retirada rápida registrada para {nome}.")

    def retirada_maxima_consulta(self):
        chave_material = getattr(self, "material_selecionado_chave", "")
        nome = self.consulta_material_var.get().strip()
        if chave_material == "" or nome == "Nenhum material selecionado" or not nome:
            messagebox.showwarning("Seleção obrigatória", "Selecione um material na tabela antes de movimentar.")
            return

        item = self.estoque["itens"].get(chave_material)
        if not item:
            messagebox.showerror("Erro", "Material não encontrado no estoque.")
            return
        quantidade = item["quantidade"]

        if quantidade <= 0:
            messagebox.showwarning("Sem estoque", "Esse material já está zerado no estoque.")
            return

        motivo = self.consulta_motivo.get().strip() or "Retirada da quantidade máxima"
        item["quantidade"] = 0
        self.registrar_movimentacao(chave_material, item.get("nome", chave_material), "retirada", quantidade, motivo)
        self.atualizar_tela_consulta()
        self.mostrar_log_do_material(None)
        self.consulta_motivo.delete(0, tk.END)
        self.consulta_quantidade.delete(0, tk.END)
        self.consulta_quantidade.insert(0, "1")
        self.atualizar_status(f"Quantidade máxima retirada para {nome}.")
        messagebox.showinfo("Sucesso", f"Quantidade máxima retirada para {nome}.")

    def remover_item_estoque(self):
        chave_material = getattr(self, "material_selecionado_chave", "")
        nome = self.consulta_material_var.get().strip()
        if chave_material == "" or nome == "Nenhum material selecionado" or not nome:
            messagebox.showwarning("Seleção obrigatória", "Selecione um material na tabela antes de remover.")
            return

        senha_configurada = self.obter_senha_remocao()
        if not senha_configurada:
            messagebox.showwarning(
                "Configuração incompleta",
                "Defina a variável de ambiente ESTOQUE_SENHA_REMOCAO ou configure a senha em configuracao.json antes de remover itens.",
            )
            return

        senha = simpledialog.askstring("Autorização", "Digite a senha para remover o item do estoque:", show="*")
        if senha != senha_configurada:
            messagebox.showerror("Senha incorreta", "A remoção do item foi negada.")
            return

        item = self.estoque["itens"].get(chave_material)
        if not item:
            messagebox.showerror("Erro", "Material não encontrado no estoque.")
            return

        item_copia = item.copy()
        item_copia["log"] = list(item["log"])
        data_remocao = datetime.now().strftime(DATE_TIME_FORMAT)

        self.lixeira["itens_removidos"].append(
            {
                "nome": item.get("nome", chave_material),
                "item": item_copia,
                "removido_em": data_remocao,
            }
        )
        self.salvar_lixeira()

        self.registrar_movimentacao(chave_material, item.get("nome", chave_material), "remoção_definitiva", item["quantidade"], "Item removido do estoque e enviado para a lixeira")
        del self.estoque["itens"][chave_material]
        self.salvar_dados()

        self.atualizar_tela_consulta()
        self.consulta_material_var.set("Nenhum material selecionado")
        self.info_material.configure(state="normal")
        self.info_material.delete("1.0", tk.END)
        self.info_material.configure(state="disabled")
        self.log_material.configure(state="normal")
        self.log_material.delete("1.0", tk.END)
        self.log_material.insert("1.0", "Nenhum material selecionado.")
        self.log_material.configure(state="disabled")
        self.atualizar_status(f"Item {nome} removido do estoque e enviado para lixeira.json.")
        messagebox.showinfo("Sucesso", f"Item {nome} removido do estoque e enviado para lixeira.json.")

    def on_close(self):
        self.salvar_configuracao()
        self.salvar_dados()
        self.root.destroy()


if __name__ == "__main__":
    EstoqueApp()
