from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Escenario:
    nombre: str
    historia: str
    significado_variables: Tuple[str, ...]
    regla_original: str
    regla_nueva: str
    consecuencia_si_difieren: str
    mensaje_si_coinciden: str

    def __str__(self):
        return self.nombre
