# Servidor-de-juegos
Este es un proyecto de un servidor de juegos pensado para pasar un buen rato con amigos. 
El juego discurrirá en una red local. El ordenador que haga de servidor deberá ser conectado a un televisor y realizará las labores de administrador del juego, mostrando la parte dinámica de los mismos.
Cada jugador se conectará desde su móvil al servidor y participará en los juegos utilizando controles sencillos, con el objetivo de conseguir monedas.
Los juegos se distribuyen en rondas, y al final de cada una se repartirá un premio entre los jugadores. Para elegir el ganador, se utiliza una ruleta con los nombres de los participantes. La probabilidad de ganar de cada uno depende de las monedas que tenga. El premio que se llevará puede ser un dulce o un regalo pequeño, mediano o grande, decidiéndose esto también mediante otra ruleta. El ganador canjeará su regalo por monedas, para dejar espacio a que los otros jugadores ganen en las siguientes rondas. Si ha ganado un dulce, le costará 5 monedas. Si ha ganado un regalo, le costará 20, 30 o 40 monedas respectivamente.

La forma de ganar monedas o perder monedas depende del juego:

- Juego de la ruleta: las monedas se apuestan en una ruleta francesa de casino (con solo un 0). Esta ruleta admite apuestas de rojo-negro, par-impar, mitades, tercios, filas y números individuales. 
En este juego una ronda equivale a una tirada, por lo que tras cada tirada se repartirá un premio.

- Juego del ahorcado: los jugadores van a colaborar y competir para adivinar la misma palabra del ahorcado.
  * Ganar monedas: el/los jugadores que digan la letra más repetida en la palabra se reparten las monedas de las veces que aparezca. Cada letra encontrada equivale a 10 monedas.
  * Perder monedas: el/los jugadores que digan menos letras repetidas son ahorcados y pierden 10 veces las monedas de la longitud de la palabra menos las apariciones de las letras que han dicho.
En este juego una ronda equivale a adivinar una palabra entera.

- Juego de la democracia: los jugadores se dividen en dos equipos de colores. El suelo es una cuadrícula de cuadrados de los dos colores, repartidos de manera aleatoria. Todos los jugadores controlarán el mismo personaje, que solo podrá estar en una casilla a la vez. El objetivo es hacer que el personaje se mantenga el máximo tiempo posible en las casillas del color de tu equipo. Las rondas duran 30 segundos, y el personaje se moverá una vez por segundo. Cada jugador tendrá 3 clicks cada segundo para decidir hacia qué dirección mover el personaje. Cada click equivale a moverlo una casilla, pero el movimiento final será la suma de todas las fuerzas.
  * Ganar monedas: los jugadores del equipo ganador ganarán 5 monedas por cada segundo del resultado de la resta entre su tiempo menos el del equipo rival.
  * Perder monedas: nadie pierde (juego de recuperación de monedas). Este juego se jugará cada vez que un jugador se quede sin monedas. Si no consigue ganar se le darán 10 gratis.


- Juego del bandido doblemente armado: se crean tantas tragaperras como jugadores, cada una con una probabilidad aleatoria entre 0.2 y 0.8 de dar premios, y una probabilidad aleatoria de que el premio sea alto o bajo en caso de darlo (duplicar, triplicar o cuadruplicar la apuesta). Se pide a cada jugador que apueste las monedas que quiera a una de ellas. Al final de la ronda, se lanzan las tragaperras y se les reparten los premios a los jugadores, indicando qué tragaperras han ganado y perdido. Tras 5 apuestas se desvela a los jugadores los valores secretos de todas ellas y se vuelven a generar otras. La ronda equivale a realizar estas 5 subrondas de apuestas a las mismas tragaperras.
