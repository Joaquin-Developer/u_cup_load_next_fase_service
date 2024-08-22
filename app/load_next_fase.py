import logging
import requests
from typing import Dict, Any
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker

from app.models.enfrentamientos import Enfrentamiento
from app.core.database import engine, get_session
from app.core.config import config
from app import queries


logger = logging.getLogger()
logger.setLevel(logging.INFO)

Base = declarative_base()


def fetch_from_api(endpoint: str) -> Any:
    url = config.PRINCIPAL_API_URL + endpoint
    return requests.get(url).json()


def get_actual_fase() -> Any:
    return fetch_from_api("fase_final/fase_actual")


def get_next_fase_metadata(next_fase_id: int) -> Dict[str, Any]:
    return fetch_from_api(f"fase/{next_fase_id}")


def get_group_clasifs():
    url = config.PRINCIPAL_API_URL + "estadisticas/clasificados"
    data = requests.get(url).json()

    return {
        f"{team['grupo']}{team['equipo_posicion']}": team["equipo_id"]
        for team in data
    }


def get_insert_object(local_id: int, vis_id: int, fase_id: int) -> Enfrentamiento:
    return Enfrentamiento(
        local_id=local_id,
        visitante_id=vis_id,
        fase_id=fase_id,
        goles_local=None,
        goles_visitante=None,
        fecha=None,
        penales_local=None,
        penales_visitante=None
    )


def load_first_fase_from_groups():
    teams = get_group_clasifs()
    group_keys = sorted(set([letter[0] for letter in list(teams.keys())]))

    # combinaciones de partidos
    # siguiendo la lógica A1-B2, A2-B1, C1-D2, C2-D1, etc
    comb_ida = []
    index = 0

    while True:
        try:
            actual = group_keys[index]
            siguiente = group_keys[index + 1]
        except IndexError:
            break

        comb_ida.append((teams[f"{actual}1"], teams[f"{siguiente}2"]))
        comb_ida.append((teams[f"{actual}2"], teams[f"{siguiente}1"]))
        index += 2

    comb_vuelta = [(_tuple[-1], _tuple[0]) for _tuple in comb_ida]
    combinations = comb_ida + comb_vuelta

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    for match in combinations:
        insert = get_insert_object(match[0], match[1], 1)
        session.add(insert)
    session.commit()
    session.close()


def load_next_fase(last_completed_fase: int):
    query = text(queries.QUERY_CLASIFS_FASE.format(fase_id=last_completed_fase))
    data = []

    with get_session() as db:
        result = db.execute(query).fetchall()

    for row in result:
        dict_row = dict(zip(row._mapping.keys(), row))
        data.append(dict_row)

    teams = [team["id"] for team in data]

    comb_ida = list(zip(teams[::2], teams[1::2]))
    comb_vuelta = [(y, x) for x, y in comb_ida]

    combinations = comb_ida + comb_vuelta

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    for match in combinations:
        insert = get_insert_object(match[0], match[1], last_completed_fase + 1)
        session.add(insert)
    session.commit()
    session.close()


def verify_load_next_fase() -> bool:
    query = text(queries.QUERY_ACTUAL_FASE_FINISHED)
    with get_session() as db:
        result = db.execute(query).fetchone()[0]

    return result == 1


def main():
    """
    Funcion principal para cargar datos de la siguiente fase.
    """
    if not verify_load_next_fase():
        return {"message": "No hay fase para cargar."}

    last_completed_fase = get_actual_fase()
    last_completed_fase_id = int(last_completed_fase["id"])

    if last_completed_fase_id == 0:
        logger.info("- Ult. fase completa es FG, se cargará 1er fase")
        load_first_fase_from_groups()
    else:
        logger.info(
            f"- Ult. fase completa Id= {last_completed_fase_id}",
            " - se cargará prox fase."
        )
        load_next_fase(last_completed_fase_id)

    return {"message": "ok"}
