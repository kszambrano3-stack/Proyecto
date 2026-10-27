from dataclasses import dataclass

from reglacomprobada.modelo.ley_logica import LeyLogica
from reglacomprobada.modelo.nodo import Nodo


@dataclass(frozen=True)
class PasoSimplificacion:
    ley: LeyLogica
    resultado: Nodo
