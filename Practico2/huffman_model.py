"""
Este módulo recibe un modelo de Markov de orden 1 y construye un código Huffman
independiente para cada contexto observado.

Los contextos deterministas no necesitan bits, su único símbolo puede
representarse con un código de longitud 0.
"""

from dataclasses import dataclass, field
import heapq
from typing import Dict, Optional
from markov_model import MarkovModel


@dataclass
class HuffmanNode:
    """
    Nodo de un árbol Huffman.
    Si symbol no es None, el nodo es una hoja, por ende es un símbolo.
    Si symbol es None, el nodo es interno y tiene hijos (no es símbolo).
    """

    frequency: int
    symbol: Optional[int] = None
    left: Optional["HuffmanNode"] = None
    right: Optional["HuffmanNode"] = None


@dataclass
class ContextHuffman:
    """
    Código Huffman correspondiente a un único contexto Markov.
    codes:
        Diccionario {símbolo: código binario como string}.
    root:
        Raíz del árbol Huffman.
    deterministic:
        True si el contexto sólo tiene un símbolo posible.
    average_length:
        Longitud media del código Huffman para este contexto.
    """

    codes: Dict[int, str]
    root: Optional[HuffmanNode]
    deterministic: bool
    average_length: float


@dataclass
class HuffmanModel:
    """
    Modelo Huffman dependiente del contexto.
    contexts:
        Diccionario:
            contexto -> ContextHuffman

        donde contexto es el byte anterior.
    """

    contexts: Dict[int, ContextHuffman] = field(default_factory=dict)

    def get_code(self, context: int, symbol: int) -> str: 
        
        """"Devuelve el código Huffman del símbolo dado su contexto.
        """

        if context not in self.contexts:
            raise KeyError(
                f"No existe un código Huffman para el contexto {context}"
            )

        context_huffman = self.contexts[context]

        if symbol not in context_huffman.codes:
            raise KeyError(
                f"El símbolo {symbol} no fue observado "
                f"después del contexto {context}"
            )

        return context_huffman.codes[symbol]

    def get_context_codes(self, context: int) -> Dict[int, str]:
        """
        Devuelve todos los códigos Huffman de un contexto.
        El diccionario retornado tiene la forma:
            {símbolo: código}
        """
        if context not in self.contexts:
            raise KeyError(
                f"No existe un código Huffman para el contexto {context}"
            )
        return self.contexts[context].codes


def _build_huffman_tree(freq: Dict[int, int]) -> Optional[HuffmanNode]:
    """
    Construye el árbol Huffman a partir de un diccionario:
        {símbolo: frecuencia}
    Devuelve la raíz del árbol.
    Si freq está vacío, devuelve None.
    Caso especial:
        Si sólo existe un símbolo, la raíz es directamente una hoja.
        Ese caso se maneja posteriormente como código de longitud 0.
    """

    if not freq:
        return None


    heap = []

    counter = 0

    for symbol, frequency in freq.items():
        node = HuffmanNode(
            frequency=frequency,
            symbol=symbol,
        )

        heapq.heappush(
            heap,
            (frequency, counter, node),
        )

        counter += 1
    """
    Mientras haya más de un nodo, combinamos los dos
    de menor frecuencia.
    """
    while len(heap) > 1:
        freq1, _, node1 = heapq.heappop(heap)
        freq2, _, node2 = heapq.heappop(heap)

        parent = HuffmanNode(
            frequency=freq1 + freq2,
            symbol=None,
            left=node1,
            right=node2,
        )

        heapq.heappush(
            heap,
            (
                parent.frequency,
                counter,
                parent,
            ),
        )

        counter += 1

    return heap[0][2]

def _generate_codes(
    root: Optional[HuffmanNode],
) -> Dict[int, str]:
    """
    Recorre el árbol Huffman y genera:
        {símbolo: código binario}
    Por ejemplo:
        {
            66: "0",
            67: "10",
            68: "11"
        }
    Caso especial:
        Si el árbol tiene una única hoja, se asigna código ""
        (cadena vacía), ya que no hace falta transmitir ningún bit.
    """

    if root is None:
        return {}

    codes: Dict[int, str] = {}

    def traverse(node: HuffmanNode, prefix: str) -> None:
        # Si tiene símbolo, es una hoja.
        if node.symbol is not None:
            codes[node.symbol] = prefix
            return

        # Subárbol izquierdo -> 0
        if node.left is not None:
            traverse(node.left, prefix + "0")

        # Subárbol derecho -> 1
        if node.right is not None:
            traverse(node.right, prefix + "1")

    traverse(root, "")

    return codes


def _calculate_average_length(
    freq: Dict[int, int],
    codes: Dict[int, str],
) -> float:
    """
    Calcula la longitud media del código Huffman usando las frecuencias del modelo de Markov:
        L = sum(P(x) * longitud(código(x)))
    """

    total = sum(freq.values())

    if total == 0:
        return 0.0

    return sum(
        (count / total) * len(codes[symbol])
        for symbol, count in freq.items()
    )


def build_huffman_model(
    markov_model: MarkovModel,
) -> HuffmanModel:
    """
    Construye un modelo Huffman dependiente del contexto a partir
    de un MarkovModel.
    Para cada contexto observado por el modelo de Markov:
        contexto -> frecuencias de símbolos siguientes
                 -> árbol Huffman
                 -> códigos Huffman
    Los contextos deterministas reciben un código de longitud 0.
    Ejemplo conceptual:
        Markov:
            contexto 65:
                B -> 10
                C -> 5
                D -> 2
        Huffman:
            contexto 65:
                B -> 0
                C -> 10
                D -> 11
    """

    huffman_contexts: Dict[int, ContextHuffman] = {}

    for context, stats in markov_model.contexts.items():

        """
        Caso determinista: Sólo existe un símbolo posible después del contexto.
        
        No necesitamos transmitir bits porque el receptor,
        conociendo el modelo, sabe cuál es el símbolo.
        """
        if stats.deterministic:
            symbol = next(iter(stats.freq))

            codes = {
                symbol: ""
            }

            context_huffman = ContextHuffman(
                codes=codes,
                root=None,
                deterministic=True,
                average_length=0.0,
            )

            huffman_contexts[context] = context_huffman
            continue
        """"
        Caso general:
        construimos el árbol a partir de las frecuencias Markov.
        """
        root = _build_huffman_tree(stats.freq)

        # Obtenemos los códigos binarios.
        codes = _generate_codes(root)

        # Calculamos la longitud media.
        average_length = _calculate_average_length(
            stats.freq,
            codes,
        )

        context_huffman = ContextHuffman(
            codes=codes,
            root=root,
            deterministic=False,
            average_length=average_length,
        )

        huffman_contexts[context] = context_huffman

    return HuffmanModel(
        contexts=huffman_contexts
    )
