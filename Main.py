import customtkinter as ctk
from datetime import datetime
import Banco as db
# Configuração inicial do tema
ctk.set_appearance_mode("System")  # "System", "Dark" ou "Light"
ctk.set_default_color_theme("blue")

class TaskWidget(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da janela para parecer um Widget de Desktop
        self.title("Widget de Tarefas")
        self.geometry("340+450+100") # Largura x Altura + Posição X + Posição Y na tela
        self.overrideredirect(True)   # Remove a barra de título padrão do Windows
        
        # CORREÇÃO DO CONTORNO PRETO: Alinhamos o fundo da janela principal (self) 
        # com a cor exata do card interno para eliminar a moldura escura.
        self.configure(fg_color=("#FFFFFF", "#2C2C2E")) 

        # Torna a janela "arrastável" pela área livre
        self.bind("<Button-1>", self.iniciar_movimento)
        self.bind("<B1-Motion>", self.ao_mover)

        # Frame Principal (Simulando o card/widget da imagem)
        self.card_frame = ctk.CTkFrame(
            self, 
            corner_radius=20, 
            fg_color=("#FFFFFF", "#2C2C2E"),
            border_width=2,
            border_color=("#FFD700", "#FFD700") # Borda amarela parecida com a referência
        )
        self.card_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Cabeçalho do Widget (Título, Data, Botão Novo e Fechar)
        self.header_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=15, pady=(20, 10))

        # Data atual ao lado do título
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

        # Botão discreto para fechar o widget
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

        # Botão de Adicionar Tarefa (+) no Cabeçalho
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

        # Linha divisória sutil
        self.separador = ctk.CTkFrame(self.card_frame, height=1, fg_color=("#E5E5EA", "#3A3A3C"))
        self.separador.pack(fill="x", padx=15, pady=5)

        # Lista de Tarefas (Frame onde as checkboxes vão residir)
        self.tasks_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.tasks_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # CHAMADA DA SUA FUNÇÃO DE BUSCA (Implemente o back-end aqui)
        self.carregar_tarefas_frontend()

    def carregar_tarefas_frontend(self):
        """
        ESPAÇO PARA O SEU BACK-END:
        Aqui você deve buscar as tarefas no seu banco e repassar para o front-end desenhar.
        """
        Sessao = db.TempSessao()
        Tarefas_banco = Sessao.query(db.Tarefa).all()
            
        Lista=[]
        for itens in Tarefas_banco:
            Lista.append((itens.Id , itens.Titulo , itens.Data , itens.Completo))
            
        
      # Limpa widgets anteriores caso recarregue
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()

        self.checkboxes = []
        for id_tarefa, titulo, data, status in Lista:
            # Frame individual para cada linha (separa o checkbox da data visualmente)
            linha_task = ctk.CTkFrame(self.tasks_frame, fg_color="transparent")
            linha_task.pack(fill="x", pady=4, padx=5)

            var = ctk.BooleanVar(value=status)
            chk = ctk.CTkCheckBox(
                linha_task, 
                text=titulo, 
                variable=var,
                font=("Arial", 13),
                corner_radius=6,
                command=lambda id_t=id_tarefa, v=var: self.enviar_atualizacao_para_backend(id_t, v.get())
            )
            chk.pack(side="left", anchor="w")

            # Rótulo para exibir a data da tarefa alinhada à direita na mesma linha
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
        """Abre a janela pop-up para criar uma nova tarefa (Apenas Front)"""
        self.janela_add = ctk.CTkToplevel(self)
        self.janela_add.title("Nova Tarefa")
        self.janela_add.geometry("300x320")
        self.janela_add.resizable(False, False)
        self.janela_add.attributes("-topmost", True) # Mantém na frente

        lbl_header = ctk.CTkLabel(self.janela_add, text="Adicionar Tarefa", font=("Arial Bold", 14))
        lbl_header.pack(pady=10)

        # Campos de Entrada (Inputs)
        self.input_titulo = ctk.CTkEntry(self.janela_add, placeholder_text="Título da tarefa", width=250)
        self.input_titulo.pack(pady=8)

        self.input_desc = ctk.CTkEntry(self.janela_add, placeholder_text="Descrição", width=250)
        self.input_desc.pack(pady=8)

        self.input_data = ctk.CTkEntry(self.janela_add, placeholder_text="Data (AAAA-MM-DD)", width=250)
        self.input_data.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.input_data.pack(pady=8)

        btn_salvar = ctk.CTkButton(
            self.janela_add, 
            text="Salvar Tarefa", 
            fg_color="#28a745", 
            hover_color="#218838",
            command=self.pegar_dados_formulario
        )
        btn_salvar.pack(pady=15)

    def pegar_dados_formulario(self):
        """Pega os valores digitados nos inputs da tela flutuante"""
        titulo = self.input_titulo.get()
        descricao = self.input_desc.get()
        data = self.input_data.get()

        print(f"[BACK-END Pendente] Salvar nova tarefa -> Título: {titulo}, Desc: {descricao}, Data: {data}")

        self.janela_add.destroy()
        self.carregar_tarefas_frontend()

    # Funções para permitir arrastar a janela sem borda pela tela
    def iniciar_movimento(self, event):
        self.x_click = event.x
        self.y_click = event.y

    def ao_mover(self, event):
        x = self.winfo_x() - self.x_click + event.x
        y = self.winfo_y() - self.y_click + event.y
        self.geometry(f"+{x}+{y}")

    def enviar_atualizacao_para_backend(self, id_tarefa, status):
        """
        ESPAÇO PARA O SEU BACK-END:
        Executado sempre que o usuário marca/desmarca a checkbox.
        """
        print(f"[BACK-END Pendente] A tarefa ID {id_tarefa} teve o status alterado para: {status}")

if __name__ == "__main__":
    app = TaskWidget()
    app.mainloop()