from sqlalchemy import create_engine , Column , String , Integer ,Text , Boolean , DATE
from sqlalchemy.orm import declarative_base , sessionmaker 
import datetime


Engine = create_engine("sqlite:///Informacoes.db")
Base = declarative_base()
TempSessao = sessionmaker(bind=Engine)

class Tarefa(Base):
    __tablename__ ="Tarefas"

    Id = Column(Integer, primary_key=True , nullable=False , autoincrement=True)
    Titulo = Column(String , nullable=False)
    Descricao = Column(Text, nullable=False)
    Data =Column(DATE , nullable=False) 
    Completo= Column(Boolean , nullable=False , default=False)

    @classmethod
    def CriarTarefa(Cs,TITULO, DESCRICAO,DATA,COMPLETO):
        Sessao = TempSessao()
        
        DATA=datetime.datetime.strptime(DATA,"%d/%m/%Y").date()
        
        
        Informacoes = Cs(Titulo=TITULO , Descricao=DESCRICAO , Data=DATA , Completo=COMPLETO)
        Sessao.add(Informacoes)
        Sessao.commit()
        Sessao.close()
        
Base.metadata.create_all(Engine)


