"""
markov_model.py
================
Tiene una única función de entrada, `build_markov_model(data: bytes)`,
que recibe los bytes originales y devuelve el modelo estadístico de la 
fuente: para cada contexto (byte anterior) observado, las frecuencias 
y probabilidades condicionales de los símbolos que lo siguieron, si ese 
contexto es determinista, y su entropía condicional.

"""

from dataclasses import dataclass, field
from math import log2
from typing import Dict, Optional


@dataclass
class ContextStats:
    """Estadística condicional de un único contexto (byte anterior)."""

    freq: Dict[int, int]       # {símbolo: cantidad de veces observado}
    total: int                 # cantidad total de observaciones de este contexto
    prob: Dict[int, float]     # {símbolo: probabilidad condicional P(símbolo | contexto)}
    deterministic: bool        # True si sólo se observó 1 símbolo posible
    entropy: float             # H(X | contexto), en bits (0.0 si deterministic)


@dataclass
class MarkovModel:
    """
    Modelo de Markov de orden `order` estimado a partir de una fuente de
    `size` bytes. `contexts` sólo incluye los contextos que efectivamente
    aparecieron en los datos (representación dispersa: con 256 contextos
    posibles, la mayoría de los archivos reales no los usa todos).
    """

    order: int
    size: int
    first_byte: Optional[int]          # None si size == 0 (no hay primer byte)
    contexts: Dict[int, ContextStats] = field(default_factory=dict)

    def entropy_condicional(self) -> float:
        """
        H(X | contexto) global de la fuente, ponderando la entropía de
        cada contexto por su probabilidad estacionaria empírica
        (frecuencia relativa de aparición de ese contexto sobre el total
        de transiciones). Ver Práctico 3, ejercicio de fuentes de Markov.
        """
        total_transiciones = sum(c.total for c in self.contexts.values())
        if total_transiciones == 0:
            return 0.0
        return sum(
            (c.total / total_transiciones) * c.entropy
            for c in self.contexts.values()
        )


def build_markov_model(data: bytes) -> MarkovModel:
    """
    Recibe los bytes originales y devuelve el `MarkovModel` de orden 1 
    estimado a partir de ellos.

    Construcción:
      - El contexto de data[i] es data[i-1] (el byte inmediatamente
        anterior); por eso data[0] no tiene contexto y se guarda aparte
        en `first_byte`.
      - Para cada contexto se cuenta la frecuencia empírica de cada
        símbolo que lo siguió en todo el archivo (una única pasada).
      - Un contexto es "determinista" si sólo tuvo un símbolo siguiente
        posible en todo el archivo (entropía condicional exactamente 0).
    """
    size = len(data)
    first_byte = data[0] if size > 0 else None

    raw_freq: Dict[int, Dict[int, int]] = {}
    for i in range(1, size):
        ctx = data[i - 1]
        sym = data[i]
        bucket = raw_freq.setdefault(ctx, {})
        bucket[sym] = bucket.get(sym, 0) + 1

    contexts: Dict[int, ContextStats] = {}
    for ctx, freq in raw_freq.items():
        total = sum(freq.values())
        prob = {sym: count / total for sym, count in freq.items()}
        deterministic = len(freq) == 1
        entropy = 0.0 if deterministic else -sum(p * log2(p) for p in prob.values())
        contexts[ctx] = ContextStats(
            freq=freq,
            total=total,
            prob=prob,
            deterministic=deterministic,
            entropy=entropy,
        )

    return MarkovModel(order=1, size=size, first_byte=first_byte, contexts=contexts)
