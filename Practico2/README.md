# Markov de orden 1 + Huffman dependiente

Este módulo implementa la parte de modelado estadístico y codificación Huffman del compresor.

El esquema utilizado es:

```text
Archivo a comprimir
      |
      v
Modelo de Markov de orden 1
      |
      v
Frecuencias de cada símbolo según su contexto
      |
      v
Huffman independiente para cada contexto
      |
      v
Códigos binarios utilizados por el compresor
```

## 1. Modelo de Markov

El modelo utilizado es un **Markov de orden 1**. Esto significa que el símbolo actual se modela dependiendo únicamente del byte anterior.

Para una secuencia:

```text
A B A B A C
```

se consideran las transiciones:

```text
A -> B
B -> A
A -> B
B -> A
A -> C
```

El primer byte no tiene contexto y se almacena separadamente como `first_byte`.

Para cada contexto se almacenan:

* `freq`: frecuencia de cada símbolo que apareció después del contexto.
* `total`: cantidad total de transiciones desde ese contexto.
* `prob`: probabilidad de cada símbolo.
* `deterministic`: indica si solamente apareció un símbolo posible.
* `entropy`: entropía condicional del contexto.

Por ejemplo:

```text
Contexto A:

B: 10
C: 5
D: 2
```

significa que, cuando el byte anterior es `A`, el siguiente byte fue `B` 10 veces, `C` 5 veces y `D` 2 veces.

El modelo se construye mediante:

```python
from markov_model import build_markov_model

markov = build_markov_model(data)
```

donde `data` es un objeto `bytes`.

## 2. Huffman dependiente del contexto

A partir del modelo de Markov se construye un árbol Huffman independiente para cada contexto.

Por ejemplo, si:

```text
Contexto A:

B: 10
C: 5
D: 2
```

el algoritmo Huffman construye un código que asigna códigos más cortos a los símbolos más frecuentes. Un resultado posible es:

```text
B -> 0
C -> 10
D -> 11
```

Por lo tanto, el código utilizado para un símbolo depende de su contexto.

El mismo símbolo puede tener códigos diferentes dependiendo del byte anterior.

### Contextos deterministas

Si un contexto solamente puede ser seguido por un único símbolo:

```text
B -> A
```

entonces no es necesario transmitir ningún bit, porque conociendo el contexto el siguiente símbolo ya está determinado.

En este caso el código es:

```text
A -> ""
```

donde `""` representa un código de longitud cero.

## 3. Construcción del modelo Huffman

Una vez construido el modelo Markov:

```python
from huffman_model import build_huffman_model

huffman = build_huffman_model(markov)
```

También puede hacerse directamente:

```python
from markov_model import build_markov_model
from huffman_model import build_huffman_model

data = b"ABABABACACAC"

markov = build_markov_model(data)
huffman = build_huffman_model(markov)
```

El objeto `huffman` contiene los códigos Huffman de todos los contextos observados.

## 4. Obtener un código

Para obtener el código de un símbolo teniendo en cuenta su contexto:

```python
code = huffman.get_code(context, symbol)
```

Por ejemplo:

```python
code = huffman.get_code(ord("A"), ord("B"))
```

Si el contexto es `A` y el símbolo es `B`, se devuelve el código Huffman correspondiente a la transición `A -> B`.

También se pueden obtener todos los códigos de un contexto:

```python
codes = huffman.get_context_codes(ord("A"))
```

que devuelve un diccionario:

```python
{
    66: "0",
    67: "1"
}
```

Los números son los valores de los bytes en ASCII:

```text
65 = A
66 = B
67 = C
```

Internamente se mantienen los valores `0..255`, ya que el compresor trabaja con bytes y no solamente con caracteres ASCII.

## 5. Verificación

El archivo:

```text
prueba_huffman_markov.py
```

permite comprobar que el modelo Markov y los códigos Huffman se están construyendo correctamente.

Para una entrada como:

```python
data = b"ABABABACACAC"
```

se obtiene conceptualmente:

```text
Contexto: 65 ('A')
Determinista: False
Longitud media: 1.0000
  66 ('B') -> '0'
  67 ('C') -> '1'

Contexto: 66 ('B')
Determinista: True
Longitud media: 0.0000
  65 ('A') -> ''

Contexto: 67 ('C')
Determinista: True
Longitud media: 0.0000
  65 ('A') -> ''
```

Esto verifica que:

* `A` puede ser seguido por `B` o `C`, por lo que necesita un código Huffman.
* `B` siempre es seguido por `A`, por lo que no necesita bits.
* `C` siempre es seguido por `A`, por lo que tampoco necesita bits.

