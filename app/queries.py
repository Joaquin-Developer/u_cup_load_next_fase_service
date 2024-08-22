"""
SQL Queries para usar con SQLAlchemy
"""

QUERY_ACTUAL_FASE_FINISHED = """
    select
        case
            when (
                select count(*) as total from enfrentamientos where goles_local is NULL
            ) > 0 then 0 
            else 1
        end as load_next_fase
"""

QUERY_CLASIFS_FASE = """
    with resultados as (
        SELECT
            loc.nombre AS e_1,
            (ida.goles_local + vuelta.goles_visitante) AS goles_eq_1,
            COALESCE(vuelta.penales_visitante, 0) AS penales_eq_1,
            vis.nombre AS e_2,
            (ida.goles_visitante + vuelta.goles_local) AS goles_eq_2,
            COALESCE(vuelta.penales_local, 0) AS penales_eq_2
        FROM
            enfrentamientos ida
        JOIN enfrentamientos vuelta ON ida.fase_id = vuelta.fase_id
            AND ida.local_id = vuelta.visitante_id
            AND ida.visitante_id = vuelta.local_id
            AND ida.id < vuelta.id -- Asumiendo que el ID de la ida es menor al de la vuelta
        JOIN equipos loc ON ida.local_id = loc.id
        JOIN equipos vis ON ida.visitante_id = vis.id
        WHERE
            ida.fase_id = {fase_id}
            AND ida.goles_local IS NOT NULL
            AND vuelta.goles_local IS NOT NULL
        ORDER BY
            ida.id ASC
    )
    select
        case
            when (r.goles_eq_1 + r.penales_eq_1) > (r.goles_eq_2 + r.penales_eq_2) then e_1
            else e_2
        end as clasificado,
        e.id
    from resultados r
    join equipos e on
        case
            when (r.goles_eq_1 + r.penales_eq_1) > (r.goles_eq_2 + r.penales_eq_2) then e_1
            else e_2
        end = e.nombre
"""


# QUERY_CLASIFS_FASE = """
#     with resultados as (
#         select distinct
#             greatest(local.nombre, vis.nombre) as e_1,
#             (ida.goles_local + vuelta.goles_visitante) as goles_eq_1,
#             coalesce(vuelta.penales_local, 0) as penales_eq_1,
#             (ida.goles_visitante + vuelta.goles_local) as goles_eq_2,
#             coalesce(vuelta.penales_visitante, 0) as penales_eq_2,
#             least(local.nombre, vis.nombre) as e_2
#         from
#             fases f
#             join enfrentamientos ida on f.id = ida.fase_id
#             join enfrentamientos vuelta on f.id = vuelta.fase_id
#             join equipos local on ida.local_id = local.id
#             join equipos vis on ida.visitante_id = vis.id
#         where
#             f.id = {fase_id}
#             and ida.local_id = vuelta.visitante_id
#             and ida.visitante_id = vuelta.local_id
#             and ida.goles_local is not null
#             and vuelta.goles_local is not null
#         group by
#             greatest(local.nombre, vis.nombre),
#             least(local.nombre, vis.nombre)
#         order by ida.id asc
#     )
#     select
#         case
#             when (r.goles_eq_1 + r.penales_eq_1) > (r.goles_eq_2 + r.penales_eq_2) then e_1
#             else e_2
#         end as clasificado,
#         e.id
#     from resultados r
#     join equipos e on
#         case
#             when (r.goles_eq_1 + r.penales_eq_1) > (r.goles_eq_2 + r.penales_eq_2) then e_1
#             else e_2
#         end = e.nombre
# """
