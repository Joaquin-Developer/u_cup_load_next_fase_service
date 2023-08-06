from sqlalchemy import Column, Integer, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Enfrentamiento(Base):
    __tablename__ = 'enfrentamientos'
    id = Column(Integer, primary_key=True)
    local_id = Column(Integer)
    visitante_id = Column(Integer)
    fase_id = Column(Integer)
    goles_local = Column(Integer, nullable=True)
    goles_visitante = Column(Integer, nullable=True)
    fecha = Column(Date, nullable=True)
    penales_local = Column(Integer, nullable=True)
    penales_visitante = Column(Integer, nullable=True)
