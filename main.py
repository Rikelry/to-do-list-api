from datetime import date, datetime
from http import HTTPStatus
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Path, Query

from schemas import (
    TarefaAtualizar,
    TarefaBD,
    TarefaCriar,
    TarefaPublic,
    TarefasResponse,
)


app = FastAPI()

banco: list[TarefaBD] = []


@app.get("/")
def home():
    return {"mensagem": "API de Lista de Tarefas funcionando!"}


@app.get("/tarefas", response_model=TarefasResponse)
def listar_tarefas(
    concluida: bool | None = None,
    tag: str | None = None,
    titulo: str | None = None,
    ordenar_por: Literal[
        "id",
        "titulo",
        "data_criacao",
        "data_atualizacao",
    ] | None = None,
    ordem: Literal["asc", "desc"] = "asc",
    pagina: Annotated[int, Query(ge=1)] = 1,
    limite: Annotated[int, Query(ge=1, le=100)] = 10,
    data_inicio: date | None = None,
    data_fim: date | None = None,
):
    tarefas = banco.copy()

    # Filtro por situação
    if concluida is not None:
        tarefas = [
            tarefa
            for tarefa in tarefas
            if tarefa.concluida == concluida
        ]

    # Filtro por tag
    if tag is not None:
        tarefas = [
            tarefa
            for tarefa in tarefas
            if tag in tarefa.tags
        ]

    # Filtro por título
    if titulo is not None:
        tarefas = [
            tarefa
            for tarefa in tarefas
            if titulo.lower() in tarefa.titulo.lower()
        ]

    # Filtro por período de criação
    if data_inicio is not None:
        tarefas = [
            tarefa
            for tarefa in tarefas
            if tarefa.data_criacao.date() >= data_inicio
        ]

    if data_fim is not None:
        tarefas = [
            tarefa
            for tarefa in tarefas
            if tarefa.data_criacao.date() <= data_fim
        ]

    # Ordenação
    if ordenar_por is not None:
        if ordenar_por == "id":
            chave = lambda tarefa: tarefa.id

        elif ordenar_por == "titulo":
            chave = lambda tarefa: tarefa.titulo.lower()

        elif ordenar_por == "data_criacao":
            chave = lambda tarefa: tarefa.data_criacao

        else:
            chave = lambda tarefa: tarefa.data_atualizacao

        tarefas = sorted(
            tarefas,
            key=chave,
            reverse=ordem == "desc",
        )

    # Paginação
    total = len(tarefas)

    inicio = (pagina - 1) * limite
    fim = inicio + limite

    tarefas_paginadas = tarefas[inicio:fim]

    return {
        "pagina": pagina,
        "limite": limite,
        "total": total,
        "tarefas": tarefas_paginadas,
    }


@app.get(
    "/tarefas/{id}",
    response_model=TarefaPublic,
    status_code=HTTPStatus.OK,
)
def buscar_tarefa(id: Annotated[int, Path(ge=1)]):
    for tarefa in banco:
        if tarefa.id == id:
            return tarefa

    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail="Tarefa não encontrada",
    )


@app.post("/tarefas", response_model=TarefaPublic, status_code=HTTPStatus.CREATED,)
def criar_tarefa(tarefa: TarefaCriar):
    if banco:
        novo_id = max(t.id for t in banco) + 1
    else:
        novo_id = 1

    agora = datetime.now()

    nova_tarefa = TarefaBD(
        id=novo_id,
        titulo=tarefa.titulo,
        descricao=tarefa.descricao,
        tags=tarefa.tags,
        concluida=False,
        data_criacao=agora,
        data_atualizacao=agora,
    )

    banco.append(nova_tarefa)

    return nova_tarefa


@app.put("/tarefas/{id}", response_model=TarefaPublic,)
def atualizar_tarefa(id: Annotated[int, Path(ge=1)], tarefa: TarefaAtualizar,):
    for i, tarefa_existente in enumerate(banco):
        if tarefa_existente.id == id:
            tarefa_atualizada = TarefaBD(
                id=id,
                titulo=tarefa.titulo,
                descricao=tarefa.descricao,
                concluida=tarefa.concluida,
                tags=tarefa.tags,
                data_criacao=tarefa_existente.data_criacao,
                data_atualizacao=datetime.now(),
            )

            banco[i] = tarefa_atualizada

            return tarefa_atualizada

    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail="Tarefa não encontrada",
    )


@app.delete("/tarefas/{id}", status_code=HTTPStatus.NO_CONTENT,)
def deletar_tarefa(id: Annotated[int, Path(ge=1)]):
    for i, tarefa in enumerate(banco):
        if tarefa.id == id:
            del banco[i]
            return

    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail="Tarefa não encontrada",
    )

