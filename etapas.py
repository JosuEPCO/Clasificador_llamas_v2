"""Etapas de la cronología dentaria en llamas, en orden cronológico."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Etapa:
    clave: str              # Nombre de la clase en el modelo YOLO
    nombre: str
    categoria: str | None
    edad: str
    edad_corta: str
    detalle: str
    permanentes: int        # Incisivos inferiores permanentes (de 6)
    desgaste: bool = False  # Dientes de leche con desgaste visible


ETAPAS = (
    Etapa("DL_menor", "Diente de leche menor", "Cría", "Menor a 1 año", "< 1 año",
          "Dientes de leche sin desgaste", 0),
    Etapa("DL_Mayor", "Diente de leche mayor", "Tui", "1 a 2 años", "1–2 años",
          "Dientes de leche con desgaste", 0, desgaste=True),
    Etapa("2D", "2 dientes", None, "2.5 a 3 años", "2.5–3 años",
          "Primer par de incisivos permanentes", 2),
    Etapa("4D", "4 dientes", None, "3.5 a 4 años", "3.5–4 años",
          "Segundo par de incisivos permanentes", 4),
    Etapa("BLL", "Boca llena", None, "4 años y medio a más", "≥ 4.5 años",
          "Todos los incisivos permanentes", 6),
)

POR_CLAVE = {etapa.clave: etapa for etapa in ETAPAS}


def buscar(clave):
    """Devuelve la etapa de una clase del modelo, o una genérica si no se reconoce."""
    return POR_CLAVE.get(clave) or Etapa(clave, clave, None, "No determinada", "—", "", 0)
