from sqlalchemy import Column, Integer, String, Boolean, Date, Time
from database import Base

class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String, nullable=False)
    unificado = Column(Boolean, default=False)
    sisplan_web = Column(Boolean, default=False)
    data_conversao = Column(Date, nullable=False)
    ultimo_dia_trabalho = Column(String)
    horario_trabalho = Column(Time)
    valor = Column(String)
    conexao = Column(String)
    concluido = Column(Boolean, default=False)
