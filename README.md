# Servidor-de-juegos
Este es un proyecto de un servidor de juegos pensado para pasar un buen rato con amigos. 
Un ordenador enchufado a un televisor hará de host, en el que aparecerá la parte dinámica de los juegos.
Cada persona se conectará desde su teléfono al servidor y participará con controles sencillos en las pruebas. Si tiene éxito, logrará conseguir monedas.
Al final de cada ronda de cada juego se reparte un regalo entre los jugadores. Para elegir el ganador, se crea una ruleta con los nombres de los participantes. 
La probabilidad de ganar de cada uno depende de las monedas que tenga. El que gane canjeará su regalo por monedas, para dejar espacio a que los otros jugadores ganen en las siguientes rondas. Si el regalo es un dulce, le costará una moneda. Si es un regalo, le costará 3 monedas. Si se iba a quedar sin monedas, no se le descuentan.

La forma de ganar monedas o perder monedas depende del juego:

- Juego de la ruleta: las monedas se apuestan en una ruleta francesa de casino (con solo un 0). Esta ruleta admite apuestas de rojo-negro, par-impar, mitades, tercios, filas y números individuales.

- Juego del ahorcado: los jugadores van a colaborar y competir para adivinar la misma palabra del ahorcado.
  * Ganar monedas: el/los jugadores que digan la letra más repetida en la palabra se reparten las monedas de las veces que aparezca.
  * Perder monedas: el/los jugadores que digan menos letras repetidas son ahorcados y pierden las monedas de la longitud de la palabra menos las apariciones de las letras que han dicho.

- Juego de la democracia: los jugadores se dividen en dos equipos de colores. El suelo es una cuadrícula de cuadrados de los dos colores, repartidos de manera aleatoria. Todos los jugadores controlarán el mismo personaje, que solo podrá estar en una casilla a la vez. El objetivo es hacer que el personaje se mantenga el máximo tiempo posible en las casillas del color de tu equipo. Las rodas duran 30 segundos, y el personaje se moverá una vez por segundo. Cada jugador tendrá 3 clicks cada segundo para decidir hacia qué dirección mover el personaje. Cada click equivale a moverlo una casilla, pero el movimiento final será la suma de todas las fuerzas.
  * Ganar monedas: los jugadores del equipo ganador ganarán una moneda por cada segundo del resultado de la resta entre su tiempo menos el del equipo rival.
  * Perder monedas: nadie pierde (juego de recuperación de monedas). Este juego se jugará cada vez que un jugador se quede sin monedas. Si no consigue ganar se de dará una gratis.


- Juego del bandido doblemente armado: se crean n tragaperras con una probabilidad aleatoria entre 0.2 y 0.8 de dar premios, y una probabilidad aleatoria de que el premio sea alto o bajo en caso de darlo (duplicar, triplicar o cuadruplicar la apuesta). Se pide a los jugadores que elijan cómo repartir sus monedas entre ellas. Al final de la ronda, se lanzan las tragaperras y se les reparten los premios a los jugadores, indicando qué tragaperras han ganado y perdido. Tras varias rondas se desvela a los jugadores los valores secretos de todas ellas y se vuelven a generar otras.
