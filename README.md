# Servidor-de-juegos
Este es un proyecto de un servidor de juegos pensado para pasar un buen rato con amigos. 
Un ordenador enchufado a un televisor hará de host, en el que aparecerá la parte dinámica de los juegos.
Cada persona se conectará desde su teléfono al servidor y participará con controles sencillos en las pruebas. Si tiene éxito, logrará conseguir monedas.
Al final de cada ronda de cada juego se reparte un regalo entre los jugadores. Para elegir el ganador, se crea una ruleta con los nombres de los participantes. 
La probabilidad de ganar de cada uno depende de las monedas que tenga. El que gane perderá monedas, para dejar espacio a que los otros jugadores ganen en las siguientes rondas.

La forma de ganar monedas o perder monedas depende del juego:

- Juego de la ruleta: las monedas se apuestan en una ruleta francesa de casino (con solo un 0). Esta ruleta admite apuestas de rojo-negro, par-impar, mitades, tercios, filas y números individuales.

- Juego del ahorcado: los jugadores van a colaborar y competir para adivinar la misma palabra del ahorcado.
  * Ganar monedas: el/los jugadores que digan la letra más repetida en la palabra se reparten las monedas de las veces que aparezca.
  * Perder monedas: el/los jugadores que digan menos letras repetidas son ahorcados y pierden las monedas de la longitud de la palabra menos las apariciones de las letras que han dicho.

- Juego de las baldosas: los jugadores se dividen en dos equipos de colores. El suelo es una cuadrícula de cuadrados de los dos colores, repartidos de manera aleatoria. 
  Todos los jugadores controlarán el mismo personaje, que solo podrá estar en una casilla a la vez. El objetivo es hacer que el personaje se mantenga en las casillas del color de tu equipo.
  Cada jugador tendrá 3 clicks cada segundo para decidir hacia qué dirección mover el personaje. Cada click equivale a moverlo una casilla, pero el movimiento final será la suma de todas las fuerzas.
