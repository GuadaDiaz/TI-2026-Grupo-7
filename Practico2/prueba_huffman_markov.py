from markov_model import build_markov_model
from huffman_model import build_huffman_model


data = b"ABABABACACAC"

markov = build_markov_model(data)
huffman = build_huffman_model(markov)


for context, context_huffman in huffman.contexts.items():
    print(f"\nContexto: {context} ({chr(context)!r})")
    print(f"Determinista: {context_huffman.deterministic}")
    print(f"Longitud media: {context_huffman.average_length:.4f}")

    for symbol, code in context_huffman.codes.items():
        print(
            f"  {symbol} ({chr(symbol)!r}) -> {code!r}"
        )