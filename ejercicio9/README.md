# Ejercicio 9 — Canal Binario Simétrico (BSC) con Sockets TCP

Simula un Canal Binario Simétrico mediante un servidor TCP (con una probabilidad de error `p` oculta) y un cliente que la descubre empíricamente, analiza la convergencia del BER por Ley de los Grandes Números, y calcula la matriz del canal, la Información Mutua y la Capacidad.

## Dependencias

Este ejercicio no requiere librerías externas. Utiliza únicamente la librería estándar de Python (módulos de sockets, entre otros).

## Ejecución

Este programa requiere ejecutar el servidor y el cliente simultáneamente. Necesitarás abrir **dos terminales diferentes**.

1. **En la Terminal 1 (Servidor):**
   ```bash
   cd ejercicio9
   python servidor.py
   ```
   El servidor quedará a la espera de nuevas conexiones.

2. **En la Terminal 2 (Cliente):**
   ```bash
   cd ejercicio9
   python cliente.py
   ```
   El cliente se conectará a `127.0.0.1:5555`, ejecutará las distintas fases (BER empírico, efecto del ruido y cálculo de métricas) y se desconectará enviando un comando de salida.

El servidor seguirá ejecutándose esperando nuevas conexiones. Para cerrarlo, presiona `Ctrl+C` en la Terminal 1.
