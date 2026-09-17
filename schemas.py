from datetime import datetime

from pydantic import BaseModel, Field


class TarefaCriar(BaseModel):
    titulo: str = Field(min_length=1)
    descricao: str
    tags: list[str] = []


class TarefaAtualizar(BaseModel):
    titulo: str = Field(min_length=1)
    descricao: str
    concluida: bool
    tags: list[str] = []


class TarefaBD(TarefaCriar):
    id: int
    concluida: bool = False
    data_criacao: datetime = Field(default_factory=datetime.now)
    data_atualizacao: datetime = Field(default_factory=datetime.now)


class TarefaPublic(BaseModel):
    id: int
    titulo: str
    descricao: str
    concluida: bool
    tags: list[str]
    data_criacao: datetime
    data_atualizacao: datetime


class TarefasResponse(BaseModel):
    pagina: int
    limite: int
    total: int
    tarefas: list[TarefaPublic]
