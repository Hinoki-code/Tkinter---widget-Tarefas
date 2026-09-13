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
        self.geometry("300x260+450+100")
        self.overrideredirect(True)
        self.configure(fg_color=("#FFFFFF", "#2C2C2E")) 

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

        data_atual = datetime.now().strftime("%d") 
        self.lbl_data = ctk.CTkLabel(
            self.header_frame, 
            text=data_atual, 
            font=("Arial Bold", 22), 
            text_color=("#FF8C00", "#FFA500")
        )
        self.lbl_data.pack(side="left", padx=(0, 10))

        self.lbl_titulo = ctk.CTkLabel(
            self.header_frame, 
            text="Lista de Tarefas", 
            font=("Arial Bold", 16), 
            text_color=("#333333", "#E1E1E6")
        )
        self.lbl_titulo.pack(side="left")

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
        self.btn_fechar.pack(side="right", padx=(2, 0))

        self.btn_adicionar = ctk.CTkButton(
            self.header_frame, 
            text="+", 
            width=25, 
            height=25, 
            fg_color="#FF8C00", 
            text_color="white",
            hover_color="#FFA500",
            font=("Arial Bold", 16),
            command=self.abrir_tela_adicao
        )
        self.btn_adicionar.pack(side="right", padx=5)

        self.separador = ctk.CTkFrame(self.card_frame, height=1, fg_color=("#E5E5EA", "#3A3A3C"))
        self.separador.pack(fill="x", padx=15, pady=5)

        self.tasks_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.tasks_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.carregar_tarefas_frontend()

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
                command=lambda id_t=id_tarefa, v=var: self.enviar_atualizacao_para_backend(id_t, v.get())
            )
            chk.pack(side="left", anchor="w", padx=(0, 5))

            lbl_titulo_tarefa = ctk.CTkLabel(
                linha_task, 
                text=titulo, 
                font=("Arial", 13),
                anchor="w"
            )
            lbl_titulo_tarefa.pack(side="left", anchor="w")
            lbl_titulo_tarefa.bind("<Double-Button-1>", lambda event, id_t=id_tarefa: self.abrir_detalhes_tarefa(id_t))

            lbl_data_tarefa = ctk.CTkLabel(
                linha_task, 
                text=str(data), 
                font=("Arial", 11), 
                text_color=("gray50", "gray40")
            )
            lbl_data_tarefa.pack(side="right", padx=5)

            self.checkboxes.append((chk, var))
            
        Sessao.close()
        
    def abrir_tela_adicao(self):
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

        self.input_data = ctk.CTkEntry(self.janela_add, placeholder_text="Data (DD-MM-YYYY)", width=250)
        self.input_data.insert(0, datetime.now().strftime("%d-%m-%Y"))
        self.input_data.pack(pady=8)

        btn_salvar = ctk.CTkButton(
            self.janela_add, 
            text="Salvar Tarefa", 
            fg_color="#28a745", 
            hover_color="#218838",
            command=self.pegar_dados_formulario
        )
        btn_salvar.pack(pady=15)

    def abrir_detalhes_tarefa(self, id_tarefa):
        Sessao = db.TempSessao()
        InfoTarefas = Sessao.query(db.Tarefa).filter_by(Id=id_tarefa).first()
        
        
        
        # Janela de detalhes com design aprimorado (divisões, cartões e estética limpa)
        self.janela_detalhes = ctk.CTkToplevel(self)
        self.janela_detalhes.title("Detalhes da Tarefa")
        self.janela_detalhes.geometry("340x380")
        self.janela_detalhes.resizable(False, False)
        self.janela_detalhes.attributes("-topmost", True)
        self.janela_detalhes.configure(fg_color=("#F4F4F6", "#1E1E1E"))

        # Cabeçalho da Janela
        lbl_detalhe_header = ctk.CTkLabel(
            self.janela_detalhes, 
            text="Detalhes da Tarefa", 
            font=("Arial Bold", 18),
            text_color=("#FF8C00", "#FFA500")
        )
        lbl_detalhe_header.pack(pady=(20, 10))

        # Container interno para estruturar os campos divididos
        container_conteudo = ctk.CTkFrame(
            self.janela_detalhes, 
            fg_color=("#FFFFFF", "#2C2C2E"),
            corner_radius=15,
            border_width=1,
            border_color=("#E5E5EA", "#3A3A3C")
        )
        container_conteudo.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Campo: Identificador / Título
        lbl_info_id = ctk.CTkLabel(container_conteudo, text=f"ID da Tarefa: #{id_tarefa}", font=("Arial Bold", 12), text_color=("gray50", "gray40"))
        lbl_info_id.pack(anchor="w", padx=15, pady=(15, 2))

        self.lbl_detalhe_titulo = ctk.CTkLabel(container_conteudo, text=InfoTarefas.Titulo, font=("Arial Bold", 15))
        self.lbl_detalhe_titulo.pack(anchor="w", padx=15, pady=(0, 10))

        # Divisor interno
        div1 = ctk.CTkFrame(container_conteudo, height=1, fg_color=("#E5E5EA", "#3A3A3C"))
        div1.pack(fill="x", padx=15, pady=5)

        # Campo: Descrição
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

        # Divisor interno
        div2 = ctk.CTkFrame(container_conteudo, height=1, fg_color=("#E5E5EA", "#3A3A3C"))
        div2.pack(fill="x", padx=15, pady=5)

        # Campo: Data
        self.lbl_detalhe_data = ctk.CTkLabel(container_conteudo, text=f"Data Limite:  {InfoTarefas.Data}", font=("Arial", 12), text_color=("#333333", "#E1E1E6"))
        self.lbl_detalhe_data.pack(anchor="w", padx=15, pady=(5, 15))

        # Botão Fechar estilizado
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

    def pegar_dados_formulario(self):
        titulo = self.input_titulo.get()
        descricao = self.input_desc.get()
        data = self.input_data.get()

        db.Tarefa.CriarTarefa(TITULO=titulo, DESCRICAO=descricao, DATA=data, COMPLETO=False)

        self.janela_add.destroy()
        self.carregar_tarefas_frontend()

    def iniciar_movimento(self, event):
        self.x_click = event.x
        self.y_click = event.y

    def ao_mover(self, event):
        x = self.winfo_x() - self.x_click + event.x
        y = self.winfo_y() - self.y_click + event.y
        self.geometry(f"+{x}+{y}")

    def enviar_atualizacao_para_backend(self, id_tarefa, status):
        print(f"[BACK-END Pendente] A tarefa ID {id_tarefa} teve o status alterado para: {status}")

if __name__ == "__main__":
    app = TaskWidget()
    app.mainloop()