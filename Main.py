import customtkinter as ctk
from datetime import datetime
import Banco as db

# Configuração inicial do tema
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class TaskWidget(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Widget de Tarefas")
        self.geometry("320x260+450+100")
        self.overrideredirect(True)

        self.configure(fg_color="#000001")
        self.attributes("-transparentcolor", "#000001")

        self.bind("<Button-1>", self.iniciar_movimento)
        self.bind("<B1-Motion>", self.ao_mover)

        self.card_frame = ctk.CTkFrame(
            self,
            corner_radius=20,
            fg_color=("#FFFFFF", "#2C2C2E"),
            border_width=2,
            border_color=("#FFD700", "#FFD700")
        )
        self.card_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.header_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=15, pady=(20, 10))

        left_header = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        left_header.pack(side="left", anchor="center")

        data_atual = datetime.now().strftime("%d")
        self.lbl_data = ctk.CTkLabel(
            left_header,
            text=data_atual,
            font=("Arial Bold", 22),
            text_color=("#FF8C00", "#FFA500")
        )
        self.lbl_data.pack(side="left", padx=(0, 10), anchor="center")

        self.lbl_titulo = ctk.CTkLabel(
            left_header,
            text="Lista de Tarefas",
            font=("Arial Bold", 16),
            text_color=("#333333", "#E1E1E6")
        )
        
        self.lbl_titulo.pack(side="left", pady=(4, 0), anchor="center")

        self.btn_fechar = ctk.CTkButton(
            self.header_frame,
            text="×",
            width=25,
            height=25,
            fg_color="transparent",
            text_color=("gray50", "gray50"),
            hover_color=("#FFCCCC", "#552222"),
            command=self.destroy
        )
        self.btn_fechar.pack(side="right", anchor="center", padx=(2, 0))

        self.btn_adicionar = ctk.CTkButton(
            self.header_frame,
            text="+",
            width=25,
            height=25,
            fg_color="#FF8C00",
            text_color="white",
            hover_color="#FFA500",
            font=("Arial Bold", 16),
            command=self.abrir_tela_adicionar
        )
        self.btn_adicionar.pack(side="right", anchor="center", padx=5)

        self.separador = ctk.CTkFrame(self.card_frame, height=1, fg_color=("#E5E5EA", "#3A3A3C"))
        self.separador.pack(fill="x", padx=15, pady=5)

        self.tasks_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.tasks_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.carregar_tarefas_frontend()

    # --- NAVEGAÇÃO E MOVIMENTAÇÃO DA JANELA ---
    def iniciar_movimento(self, event):
        self.x_click = event.x
        self.y_click = event.y

    def ao_mover(self, event):
        x = self.winfo_x() - self.x_click + event.x
        y = self.winfo_y() - self.y_click + event.y
        self.geometry(f"+{x}+{y}")

    # --- INTERFACE E CARREGAMENTO ---
    def carregar_tarefas_frontend(self):
        Sessao = db.TempSessao()
        Tarefas_banco = Sessao.query(db.Tarefa).all()

        Lista = []
        for itens in Tarefas_banco:
            Lista.append((itens.Id, itens.Titulo, itens.Data, itens.Completo))

        for widget in self.tasks_frame.winfo_children():
            widget.destroy()

        self.checkboxes = []
        for id_tarefa, titulo, data, status in Lista:
            linha_task = ctk.CTkFrame(self.tasks_frame, fg_color="transparent")
            linha_task.pack(fill="x", pady=4, padx=5)

            var = ctk.BooleanVar(value=status)
            chk = ctk.CTkCheckBox(
                linha_task,
                text="",
                width=20,
                variable=var,
                corner_radius=6,
                command=lambda id_t=id_tarefa, v=var: self.atualizar_status_tarefa(id_t, v.get())
            )
            chk.pack(side="left", anchor="w", padx=(0, 5))

            lbl_titulo_tarefa = ctk.CTkLabel(
                linha_task,
                text=titulo,
                font=("Arial", 13),
                anchor="w"
            )
            lbl_titulo_tarefa.pack(side="left", anchor="w", pady=(3, 0))
            lbl_titulo_tarefa.bind("<Double-Button-1>", lambda event, id_t=id_tarefa: self.abrir_detalhes_tarefa(id_t))

            # Botão de Excluir adicionado ao lado do Editar
            btn_excluir_linha = ctk.CTkButton(
                linha_task,
                text="Excluir",
                width=50,
                height=22,
                fg_color="#A93226",
                text_color="white",
                hover_color="#C0392B",
                font=("Arial", 11),
                command=lambda id_t=id_tarefa: self.deletar_tarefa_frontend(id_t)
            )
            btn_excluir_linha.pack(side="right", padx=2)

            # Botão de Editar
            btn_editar_linha = ctk.CTkButton(
                linha_task,
                text="Editar",
                width=50,
                height=22,
                fg_color="#3A3A3C",
                text_color="white",
                hover_color="#505052",
                font=("Arial", 11),
                command=lambda id_t=id_tarefa: self.abrir_tela_atualizar(id_t)
            )
            btn_editar_linha.pack(side="right", padx=2)

            self.checkboxes.append((chk, var))

        Sessao.close()

    # --- JANELAS SECUNDÁRIAS (MODAIS) ---
    def abrir_tela_adicionar(self):
        self.janela_add = ctk.CTkToplevel(self)
        self.janela_add.title("Nova Tarefa")
        self.janela_add.geometry("300x320")
        self.janela_add.resizable(False, False)
        self.janela_add.attributes("-topmost", True)

        lbl_header = ctk.CTkLabel(self.janela_add, text="Adicionar Tarefa", font=("Arial Bold", 14))
        lbl_header.pack(pady=10)

        self.input_titulo = ctk.CTkEntry(self.janela_add, placeholder_text="Título da tarefa", width=250)
        self.input_titulo.pack(pady=8)

        self.input_desc = ctk.CTkEntry(self.janela_add, placeholder_text="Descrição", width=250)
        self.input_desc.pack(pady=8)

        self.input_data = ctk.CTkEntry(self.janela_add, placeholder_text="Data (DD/MM/YYYY)", width=250)
        self.input_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.input_data.pack(pady=8)

        btn_salvar = ctk.CTkButton(
            self.janela_add,
            text="Salvar Tarefa",
            fg_color="#28a745",
            hover_color="#218838",
            command=self.pegar_dados_formulario
        )
        btn_salvar.pack(pady=15)

    def abrir_tela_atualizar(self, id_tarefa):
        self.janela_edit = ctk.CTkToplevel(self)
        self.janela_edit.title("Editar Tarefa")
        self.janela_edit.geometry("300x320")
        self.janela_edit.resizable(False, False)
        self.janela_edit.attributes("-topmost", True)

        lbl_header = ctk.CTkLabel(self.janela_edit, text=f"Editar Tarefa #{id_tarefa}", font=("Arial Bold", 14))
        lbl_header.pack(pady=10)

        self.input_edit_titulo = ctk.CTkEntry(self.janela_edit, placeholder_text="Novo Título", width=250)
        self.input_edit_titulo.pack(pady=8)

        self.input_edit_desc = ctk.CTkEntry(self.janela_edit, placeholder_text="Nova Descrição", width=250)
        self.input_edit_desc.pack(pady=8)

        self.input_edit_data = ctk.CTkEntry(self.janela_edit, placeholder_text="Nova Data (DD/MM/YYYY)", width=250)
        self.input_edit_data.pack(pady=8)

        btn_atualizar = ctk.CTkButton(
            self.janela_edit,
            text="Salvar Alterações",
            fg_color="#FF8C00",
            hover_color="#FFA500",
            command=lambda: self.enviar_atualizacao_para_backend(id_tarefa)
        )
        btn_atualizar.pack(pady=15)

    def abrir_detalhes_tarefa(self, id_tarefa):
        Sessao = db.TempSessao()
        InfoTarefas = Sessao.query(db.Tarefa).filter_by(Id=id_tarefa).first()

        self.janela_detalhes = ctk.CTkToplevel(self)
        self.janela_detalhes.title("Detalhes da Tarefa")
        self.janela_detalhes.geometry("340x380")
        self.janela_detalhes.resizable(False, False)
        self.janela_detalhes.attributes("-topmost", True)
        self.janela_detalhes.configure(fg_color=("#F4F4F6", "#1E1E1E"))

        lbl_detalhe_header = ctk.CTkLabel(
            self.janela_detalhes,
            text="Detalhes da Tarefa",
            font=("Arial Bold", 18),
            text_color=("#FF8C00", "#FFA500")
        )
        lbl_detalhe_header.pack(pady=(20, 10))

        container_conteudo = ctk.CTkFrame(
            self.janela_detalhes,
            fg_color=("#FFFFFF", "#2C2C2E"),
            corner_radius=15,
            border_width=1,
            border_color=("#E5E5EA", "#3A3A3C")
        )
        container_conteudo.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        lbl_info_id = ctk.CTkLabel(container_conteudo, text=f"ID da Tarefa: #{id_tarefa}", font=("Arial Bold", 12), text_color=("gray50", "gray40"))
        lbl_info_id.pack(anchor="w", padx=15, pady=(15, 2))

        self.lbl_detalhe_titulo = ctk.CTkLabel(container_conteudo, text=InfoTarefas.Titulo, font=("Arial Bold", 15))
        self.lbl_detalhe_titulo.pack(anchor="w", padx=15, pady=(0, 10))

        div1 = ctk.CTkFrame(container_conteudo, height=1, fg_color=("#E5E5EA", "#3A3A3C"))
        div1.pack(fill="x", padx=15, pady=5)

        lbl_tit_desc = ctk.CTkLabel(container_conteudo, text="Descrição:", font=("Arial Bold", 12), text_color=("gray50", "gray40"))
        lbl_tit_desc.pack(anchor="w", padx=15, pady=(5, 0))

        self.lbl_detalhe_desc = ctk.CTkLabel(
            container_conteudo,
            text=InfoTarefas.Descricao,
            font=("Arial", 13),
            wraplength=280,
            justify="left"
        )
        self.lbl_detalhe_desc.pack(anchor="w", padx=15, pady=(0, 10))

        div2 = ctk.CTkFrame(container_conteudo, height=1, fg_color=("#E5E5EA", "#3A3A3C"))
        div2.pack(fill="x", padx=15, pady=5)

        self.lbl_detalhe_data = ctk.CTkLabel(container_conteudo, text=f"Data Limite:  {datetime.strftime(InfoTarefas.Data ,'%d/%m/%Y')}", font=("Arial", 12), text_color=("#333333", "#E1E1E6"))
        self.lbl_detalhe_data.pack(anchor="w", padx=15, pady=(5, 15))

        btn_fechar_detalhes = ctk.CTkButton(
            self.janela_detalhes,
            text="Fechar",
            fg_color="#FF8C00",
            hover_color="#FFA500",
            font=("Arial Bold", 13),
            height=32,
            command=self.janela_detalhes.destroy
        )
        btn_fechar_detalhes.pack(pady=(0, 15), padx=20, fill="x")

        Sessao.close()

    # --- AÇÕES E INTEGRAÇÃO COM BANCO DE DADOS ---
    def pegar_dados_formulario(self):
        titulo = self.input_titulo.get().strip()
        descricao = self.input_desc.get().strip()
        data = self.input_data.get().strip()

        db.Tarefa.CriarTarefa(TITULO=titulo, DESCRICAO=descricao, DATA=data, COMPLETO=False)

        self.janela_add.destroy()
        self.carregar_tarefas_frontend()

    def enviar_atualizacao_para_backend(self, id_tarefa):
        Sessao = db.TempSessao()
        data_texto = self.input_edit_data.get().strip()
        DataCorreta = datetime.strptime(data_texto, "%d/%m/%Y")

        AtualizarTarefa = Sessao.query(db.Tarefa).filter_by(Id=id_tarefa).first()
        AtualizarTarefa.Titulo = self.input_edit_titulo.get().strip()
        AtualizarTarefa.Descricao = self.input_edit_desc.get().strip()
        AtualizarTarefa.Data = DataCorreta
        Sessao.commit()
        Sessao.close()
        self.janela_edit.destroy()
        self.carregar_tarefas_frontend()
        
    def atualizar_status_tarefa(self, id_tarefa, novo_status):
        Sessao = db.TempSessao()
        tarefa = Sessao.query(db.Tarefa).filter_by(Id=id_tarefa).first()
        if tarefa:
            tarefa.Completo = novo_status
            Sessao.commit()
        Sessao.close()

    def deletar_tarefa_frontend(self, id_tarefa):
        Sessao = db.TempSessao()

        DeletarTarefa = Sessao.query(db.Tarefa).filter_by(Id=id_tarefa).first()
        Sessao.delete(DeletarTarefa)
        Sessao.commit()
        Sessao.close()

        self.carregar_tarefas_frontend()


if __name__ == "__main__":
    app = TaskWidget()
    app.mainloop()