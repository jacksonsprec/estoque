import tkinter as tk
from tkinter import ttk


class ToolbarView:
    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="x", expand=True, padx=10, pady=(10, 0))

        self.status_var = tk.StringVar(value="Sistema pronto.")
        self.status_label = tk.Label(
            self.frame,
            textvariable=self.status_var,
            anchor="w",
            justify="left",
            wraplength=700,
            padx=4,
            pady=4,
        )
        self.status_label.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.botao_tema = ttk.Button(self.frame, text="Tema: Claro", command=app.alternar_tema)
        self.botao_tema.pack(side="right")

        app.toolbar = self.frame
        app.botao_tema = self.botao_tema
        app.status_var = self.status_var
        app.status_label = self.status_label
        app.widgets_tema.append(self.botao_tema)
        app.widgets_tema.append(self.status_label)


class EntradaView:
    def __init__(self, parent, app):
        frame = parent
        app.widgets_tema.append(frame)

        tk.Label(frame, text="Material existente:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        app.entrada_material_existente = ttk.Combobox(frame, state="readonly", width=48)
        app.entrada_material_existente.grid(row=0, column=1, padx=10, pady=8)
        app.entrada_material_existente.bind("<<ComboboxSelected>>", app.selecionar_material_existente)
        app.widgets_tema.append(app.entrada_material_existente)

        tk.Label(frame, text="Nome do material:").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        app.entrada_nome = tk.Entry(frame, width=50)
        app.entrada_nome.grid(row=1, column=1, padx=10, pady=8)
        app.entrada_nome.bind("<KeyRelease>", app.autopreencher_descricao)
        app.entrada_nome.bind("<FocusOut>", app.autopreencher_descricao)
        app.widgets_tema.append(app.entrada_nome)

        tk.Label(frame, text="Descrição:").grid(row=2, column=0, sticky="w", padx=10, pady=8)
        app.entrada_descricao = tk.Entry(frame, width=50)
        app.entrada_descricao.grid(row=2, column=1, padx=10, pady=8)
        app.widgets_tema.append(app.entrada_descricao)

        tk.Label(frame, text="Quantidade:").grid(row=3, column=0, sticky="w", padx=10, pady=8)
        app.entrada_quantidade = tk.Spinbox(frame, from_=1, to=100000, width=15)
        app.entrada_quantidade.grid(row=3, column=1, sticky="w", padx=10, pady=8)
        app.widgets_tema.append(app.entrada_quantidade)

        tk.Label(frame, text="Validade:").grid(row=4, column=0, sticky="w", padx=10, pady=8)
        app.entrada_validade = tk.Entry(frame, width=30)
        app.entrada_validade.grid(row=4, column=1, sticky="w", padx=10, pady=8)
        app.entrada_validade.bind("<KeyRelease>", app.formatar_validade)
        app.widgets_tema.append(app.entrada_validade)

        tk.Label(frame, text="Formato aceito: DD/MM/AAAA (digite apenas números)", fg="#6b7280").grid(row=4, column=2, sticky="w", padx=(0, 10), pady=8)

        tk.Label(frame, text="Motivo da entrada:").grid(row=5, column=0, sticky="w", padx=10, pady=8)
        app.entrada_motivo = tk.Entry(frame, width=50)
        app.entrada_motivo.grid(row=5, column=1, padx=10, pady=8)
        app.widgets_tema.append(app.entrada_motivo)

        botao_entrada = ttk.Button(frame, text="Registrar entrada", command=app.registrar_entrada)
        botao_entrada.grid(row=6, column=0, columnspan=2, pady=15)
        app.widgets_tema.append(botao_entrada)


class RetiradaView:
    def __init__(self, parent, app):
        frame = parent
        app.widgets_tema.append(frame)
        tk.Label(frame, text="Material:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        app.retirada_material = ttk.Combobox(frame, state="readonly", width=48)
        app.retirada_material.grid(row=0, column=1, padx=10, pady=8)
        app.widgets_tema.append(app.retirada_material)

        tk.Label(frame, text="Quantidade a retirar:").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        app.retirada_quantidade = tk.Spinbox(frame, from_=1, to=100000, width=15)
        app.retirada_quantidade.grid(row=1, column=1, sticky="w", padx=10, pady=8)
        app.widgets_tema.append(app.retirada_quantidade)

        tk.Label(frame, text="Motivo da retirada:").grid(row=2, column=0, sticky="w", padx=10, pady=8)
        app.retirada_motivo = tk.Entry(frame, width=50)
        app.retirada_motivo.grid(row=2, column=1, padx=10, pady=8)
        app.widgets_tema.append(app.retirada_motivo)

        botao_retirada = ttk.Button(frame, text="Registrar retirada", command=app.registrar_retirada)
        botao_retirada.grid(row=3, column=0, columnspan=2, pady=15)
        app.widgets_tema.append(botao_retirada)


class ConsultaView:
    def __init__(self, parent, app):
        frame = parent

        frame_left = ttk.Frame(frame)
        frame_left.pack(side="left", fill="y", padx=(10, 5), pady=10)
        app.widgets_tema.append(frame_left)

        scroll_canvas = tk.Canvas(frame, highlightthickness=0)
        scroll_canvas.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=10)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=scroll_canvas.yview)
        scrollbar.pack(side="right", fill="y", pady=10)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)

        frame_content = ttk.Frame(scroll_canvas)
        scroll_canvas.create_window((0, 0), window=frame_content, anchor="nw")
        frame_content.bind("<Configure>", lambda event: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))
        app.widgets_tema.append(frame_content)

        frame_center = ttk.Frame(frame_content)
        frame_center.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        frame_quick = ttk.Frame(frame_content)
        frame_quick.grid(row=0, column=1, sticky="nsew")
        frame_content.grid_columnconfigure(0, weight=1)
        frame_content.grid_columnconfigure(1, weight=1)
        app.widgets_tema.append(frame_center)
        app.widgets_tema.append(frame_quick)

        app.tree_estoque = ttk.Treeview(
            frame_left,
            columns=("material", "quantidade", "validade", "_chave_material"),
            show="headings",
            displaycolumns=("material", "quantidade", "validade"),
        )
        app.tree_estoque.heading("material", text="Material")
        app.tree_estoque.heading("quantidade", text="Quantidade")
        app.tree_estoque.heading("validade", text="Validade")
        app.tree_estoque.column("material", width=220, anchor="center")
        app.tree_estoque.column("quantidade", width=110, anchor="center")
        app.tree_estoque.column("validade", width=140, anchor="center")
        app.tree_estoque.column("_chave_material", width=0, stretch=False)
        app.tree_estoque.pack(fill="both", expand=True)
        app.tree_estoque.bind("<<TreeviewSelect>>", app.mostrar_log_do_material)
        app.widgets_tema.append(app.tree_estoque)

        tk.Label(frame_left, text="Filtrar material:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(0, 5))
        app.busca_material = tk.Entry(frame_left, width=30)
        app.busca_material.pack(fill="x", padx=10, pady=(0, 8))
        app.busca_material.bind("<KeyRelease>", app.filtrar_estoque)
        app.widgets_tema.append(app.busca_material)

        tk.Label(frame_left, text="Filtrar por validade:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(0, 5))
        app.filtro_validade = ttk.Combobox(
            frame_left,
            state="readonly",
            width=28,
            values=["Todos", "Vencendo em até 30 dias", "Vencidos", "Sem validade"],
        )
        app.filtro_validade.set("Todos")
        app.filtro_validade.pack(fill="x", padx=10, pady=(0, 8))
        app.filtro_validade.bind("<<ComboboxSelected>>", app.filtrar_estoque)
        app.widgets_tema.append(app.filtro_validade)

        tk.Label(frame_center, text="Dashboard do estoque:", font=("Arial", 10, "bold")).pack(anchor="w")
        app.dashboard_text = tk.Text(frame_center, height=8, wrap="word", state="disabled")
        app.dashboard_text.pack(fill="x", pady=(5, 10))
        app.widgets_tema.append(app.dashboard_text)

        tk.Label(frame_center, text="Alertas de validade:", font=("Arial", 10, "bold")).pack(anchor="w")
        app.alerta_validade = tk.Text(frame_center, height=7, wrap="word", state="disabled")
        app.alerta_validade.pack(fill="x", pady=(5, 10))
        app.alerta_validade.tag_configure("titulo_vencido", foreground="#b91c1c", font=("TkDefaultFont", 9, "bold"))
        app.alerta_validade.tag_configure("titulo_5", foreground="#b45309", font=("TkDefaultFont", 9, "bold"))
        app.alerta_validade.tag_configure("titulo_10", foreground="#9a6700", font=("TkDefaultFont", 9, "bold"))
        app.alerta_validade.tag_configure("titulo_15", foreground="#1d4ed8", font=("TkDefaultFont", 9, "bold"))
        app.alerta_validade.tag_configure("vencido", foreground="#b91c1c", font=("TkDefaultFont", 9, "bold"))
        app.alerta_validade.tag_configure("proximo_5", foreground="#b45309", font=("TkDefaultFont", 9, "normal"))
        app.alerta_validade.tag_configure("proximo_10", foreground="#9a6700", font=("TkDefaultFont", 9, "normal"))
        app.alerta_validade.tag_configure("proximo_15", foreground="#1d4ed8", font=("TkDefaultFont", 9, "normal"))
        app.widgets_tema.append(app.alerta_validade)

        tk.Label(frame_center, text="Dados do material selecionado:", font=("Arial", 10, "bold")).pack(anchor="w")
        app.info_material = tk.Text(frame_center, height=8, wrap="word", state="disabled")
        app.info_material.pack(fill="x", pady=(5, 10))
        app.widgets_tema.append(app.info_material)

        tk.Label(frame_quick, text="Movimentação rápida:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        app.consulta_material_var = tk.StringVar(value="Nenhum material selecionado")
        tk.Label(frame_quick, textvariable=app.consulta_material_var).pack(anchor="w")

        tk.Label(frame_quick, text="Quantidade:").pack(anchor="w", pady=(8, 2))
        app.consulta_quantidade = tk.Spinbox(frame_quick, from_=1, to=100000, width=15)
        app.consulta_quantidade.pack(anchor="w")
        app.widgets_tema.append(app.consulta_quantidade)

        tk.Label(frame_quick, text="Motivo:").pack(anchor="w", pady=(8, 2))
        app.consulta_motivo = tk.Entry(frame_quick, width=40)
        app.consulta_motivo.pack(anchor="w")
        app.widgets_tema.append(app.consulta_motivo)

        botoes_container = ttk.Frame(frame_quick)
        botoes_container.pack(fill="x", pady=(10, 5))
        app.widgets_tema.append(botoes_container)

        botao_entrada_rapida = ttk.Button(botoes_container, text="Entrada rápida", command=app.entrada_rapida_consulta)
        botao_entrada_rapida.pack(side="left", padx=(0, 5), pady=(0, 5))
        app.widgets_tema.append(botao_entrada_rapida)

        botao_retirada_rapida = ttk.Button(botoes_container, text="Retirada rápida", command=app.retirada_rapida_consulta)
        botao_retirada_rapida.pack(side="left", padx=(0, 5), pady=(0, 5))
        app.widgets_tema.append(botao_retirada_rapida)

        botao_retirada_maxima = ttk.Button(botoes_container, text="Retirar máxima", command=app.retirada_maxima_consulta)
        botao_retirada_maxima.pack(side="left", padx=(0, 5), pady=(0, 5))
        app.widgets_tema.append(botao_retirada_maxima)

        botao_remover = ttk.Button(botoes_container, text="Remover item", command=app.remover_item_estoque)
        botao_remover.pack(side="left", padx=(0, 5), pady=(0, 5))
        app.widgets_tema.append(botao_remover)

        botao_exportar_pdf = ttk.Button(botoes_container, text="Exportar PDF", command=app.exportar_relatorio_pdf)
        botao_exportar_pdf.pack(side="left", pady=(0, 5))
        app.widgets_tema.append(botao_exportar_pdf)


class LogView:
    def __init__(self, parent, app):
        frame = parent
        app.widgets_tema.append(frame)

        tk.Label(frame, text="Log do material:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        app.log_material = tk.Text(frame, height=24, wrap="word", state="disabled")
        app.log_material.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        app.widgets_tema.append(app.log_material)
