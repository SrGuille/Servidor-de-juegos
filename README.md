# Servidor-de-juegos
Este es un proyecto de un servidor de videojuegos pensado para pasar un buen rato con amigos en Navidad.

CONDICIONES PREVIAS: Se recomienda ser entre 5 y 15 personas. Para participar todos deben traer dulces y 3 regalos de precios ascendentes, llamados regalo pequeño, mediano y grande.

SERVIDOR:El juego discurrirá en una red local. Idealmente el ordenador que haga de servidor deberá ser conectado a un televisor que todos puedan ver para mostrar los escenarios de los juegos. Ese ordenador además realizará la labor de administrador del juego.

JUGADORES: Cada jugador se conectará desde su móvil al servidor y participará en los juegos utilizando controles sencillos, con el objetivo de conseguir monedas.

DINÁMICA: Todo el rato se juega a uno de los juegos y después se reparte un premio. Salvo contadas excepciones (explicadas después) el administrador elegirá qué juegos ocurrirán, pudiendo elegir que un juego se repita varias veces seguidas (siempre con premios entre partidas).

PREMIOS/ECONOMÍA: Para elegir al ganador del premio, se utiliza una ruleta con los nombres de los participantes. Esta es dinámica, ya que la probabilidad de ganar de cada uno depende directamente de las monedas que tenga en comparación con los demás. El premio que se llevará puede ser un dulce o un regalo pequeño, mediano o grande, decidiéndose esto también mediante otra ruleta. El ganador canjeará su regalo por monedas, para dejar espacio a que los otros jugadores ganen en las siguientes ocasiones. Si ha ganado un dulce, le costará 5 monedas. Si ha ganado un regalo, le costará 20, 30 o 40 monedas respectivamente.

JUEGOS: La forma de ganar monedas o perder monedas depende del juego:

- Juego de la ruleta: las monedas se apuestan en una ruleta francesa de casino (con solo un 0). Esta ruleta admite apuestas de rojo-negro, par-impar, mitades, tercios, filas y números individuales. 
El juego solo dura una tirada, por lo que tras cada tirada se repartirá un premio.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Juego de la democracia: los jugadores se dividen en dos equipos de colores de forma aleatoria. Si los jugadores son impares un equipo tendrá un jugador menos, pero esto no tiene que ser necesariamente malo para ese equipo.

  El suelo es una cuadrícula de cuadrados de los dos colores, repartidos de manera aleatoria. Todos los jugadores de la partida controlarán al mismo personaje, que solo podrá estar en una casilla a la vez. El objetivo de los jugadores es hacer que el personaje se mantenga el máximo tiempo posible en las casillas del color de su equipo. El juego dura 30 segundos, y el personaje se moverá una vez por segundo. El movimiento será la suma de fuerzas de la decisión democrática emitida entre todos los jugadores de ambos equipos. Cada jugador tendrá 1 click cada segundo para decidir hacia qué dirección mover el personaje, pudiendo abstenerse a moverlo. El equipo ganador es aquel que mantenga al personaje en su color más segundos que el rival, pudiendo empatar.

  Al terminar el juego los jugadores del equipo ganador ganarán 5 monedas por cada segundo del resultado de la resta entre su tiempo menos el del equipo rival. Nadie pierde monedas, de manera que es un juego de recuperación de monedas. Este juego se jugará cada vez que un jugador se quede sin monedas. Si no consigue ganar se le darán 10 gratis.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

El año que viene estarán disponibles:

- Juego del ahorcado: es una adaptación del juego tradicional del ahorcado donde los jugadores van a colaborar y competir para adivinar la misma frase. Se adivinan frases y no palabras para que sea más largo y difícil al haber muchos jugadores, al estilo de La Ruleta de la Suerte. En el juego tradicional se acerca la horca si el jugador dice una letra que no está en la palabra. En este caso será diferente, y se acercará la horca para todo el grupo si más de 1/4 de los jugadores dice una letra que no está en la frase. Las frases estarán generadas por ChatGPT, y todas serán oraciones en tono de broma/hipérbole de entre 10 y 12 palabras, pudiendo pedirle que haya muchas apariciones de una cierta letra poco común para hacerlo más interesante y los nombres de algunos jugadores como protagonistas.
  
  El juego dura hasta que se adivine una frase entera o que acaben los turnos del ahorcado. El juego está compuesto de pasos donde los jugadores dirán cada uno una letra. El jugador o los jugadores que hayan elegido la letra que más veces aparece en la frase entre las votadas en un cierto paso se reparten las monedas de las veces que aparezca y esa será la letra que se hará pública. En el caso de empate entre varias se revelan todas ellas. Cada letra encontrada equivale a 10 monedas, por lo que este premio se reparte equitativamente entre todos los que la hayan dicho, redondeando a la alza. De esta manera se recompensa a los jugadores que digan una letra arriesgada que sí esté muy repetida, ya que se quedarían el premio para ellos solos. Los jugadores que hayan elegido otras letras distintas a la ganadora no sabrán si su letra estaba en la palabra, como mucho sabrán que estaba menos repetida que la seleccionada y si se ha acercado la horca pueden pensar que es porque no estaba la suya.

  El final del juego llega cuando o se ha adivinado la frase o se han agotado las 5 vidas para que llegue la horca. En ese caso serán ahorcados aquel o aquellos jugadores que hayan dicho las letras menos repetidas son ahorcados y pierden las monedas de la longitud de la frase menos las apariciones de las letras que han dicho. De esta manera acertar la frase entre todos beneficia a aquellos jugadores menos afortunados con las letras, ya que no tendrían castigo.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Juego de las tragaperras secretas: se crean tantas tragaperras como jugadores, cada una con una probabilidad aleatoria entre 0.2 y 0.8 de dar premios, y una propiedad multiplicativa de la cantidad de premio (duplicar, triplicar o cuadruplicar la apuesta) asignada aleatoriamente de forma equiprobable. Ambas propiedades son secretas a todos los jugadores y se revelarán al final del juego. Los jugadores solo concerán el valor multiplicativo de las máquinas a las que apuesten si ganan a ellas fijándose en la cantidad de monedas que reciben.

  Un juego son 7 apuestas de todos los jugadores, y en cada una se pide a cada jugador que apueste las monedas que quiera a una de ellas. Después de que todos apuesten cada jugador verá en su móvil cuánto dinero ha ganado su apuesta, y en la tele a qué tragaperras han apostado los demás en esa ocasión. Además, también aparecerá a modo de recordatorio cuántas personas han apostado a cada máquina a lo largo del juego. De esta manera los jugadores se fijarán en qué personas repiten las apuestas a la misma máquina y qué máquinas son las más populares y podrán decidir si cambian a esa.

AGRADECIMIENTOS (de Guille): 
- A Toña por ayudar con la programación, ideas y apoyo moral.
- A Florin por realizar el diseño de la mayoría de pantallas con temática navideña (y pese a eso no haber jugado).
- A Carmen por hacer ilustraciones que tristemente no pudieron ser incluídas, pero que serán tenidas en cuenta para el año que viene.
- A Toña y a Juanda por aguantar mis fantasías sobre los juegos.

EDICIÓN 2O22: Jugamos Toña, Juanda, Carmen, Sonia, Pablo, Marcos IA, Marcos Chelo, Nayla y Guille. Fue divertido, pero se hizo tedioso por deadlocks en el login y petadas después de jugar al juego de la democracia que hacía que hubiera que reiniciar la partida y como no había base de datos había que reiniciar las monedas, hay que crear una que lleve todos los datos de la partida por su hubiera problemas. Se hizo tedioso que había demasiada probabilidad de que tocara dulce (40%), el año que viene se bajará al 25%. Además, los usuarios de iPhone no veían bien los controles del juego de la democracia. Todo esto se debió a las prisas del desarrollo y no haber testeado la partida con muchas personas como estaba planeado, el año que viene debe hacerse así. A nivel de arquitectura web, es necesario incluirle sockets en vez de hacer polling. Sería conveniente configurar un servidor DNS para crear un dominio para la página.
