# Servidor-de-juegos
Este es un proyecto de un servidor de videojuegos pensado para pasar un buen rato con amigos en Navidad.

CONDICIONES PREVIAS: Se recomienda ser entre 5 y 15 personas. Para participar todos deben traer dulces y 3 regalos de precios ascendentes, llamados regalo pequeño, mediano y grande.

SERVIDOR: El juego discurrirá en una red local. Idealmente el ordenador que haga de servidor deberá ser conectado a un televisor que todos puedan ver para mostrar los escenarios de los juegos. Ese ordenador además realizará la labor de administrador del juego.

JUGADORES: Cada jugador se conectará desde su móvil al servidor y participará en los juegos utilizando controles sencillos, con el objetivo de conseguir monedas. Todos comienzan con 200 monedas.

DINÁMICA: Durante todo el tiempo de juego todos los jugadores juegan a uno de los juegos y después se reparte un premio a uno de ellos. El administrador elegirá qué juegos ocurrirán a continuación, pudiendo elegir que un juego se repita varias veces seguidas o elegir que ocurran varias rondas de juegos aleatorios (siempre con premios entre partidas). La única excepción ocurre cuando algún jugador o jugadores se quedan sin monedas tras un juego o premio, en cuyo caso ocurrirá obligatoriamente un juego gratuito (democracia o ahorcado), donde no hacen falta monedas para jugar. Si tras ese juego alguno de los arruinados no ha ganado nada, se le darán 10 monedas gratis.

PREMIOS/ECONOMÍA: El ganador del premio no es el ganador del juego, sino que se utiliza una ruleta con los nombres de los participantes. Esta es dinámica, ya que la probabilidad de ganar de cada uno depende directamente de las monedas que tenga en comparación con los demás. El premio que se llevará puede ser un dulce o un regalo pequeño, mediano o grande, decidiéndose esto también mediante otra ruleta. El ganador canjeará su regalo por monedas, para dejar espacio a que los otros jugadores ganen en las siguientes ocasiones. Si ha ganado un dulce, le costará 5 monedas. Si ha ganado un regalo, le costará 20, 30 o 40 monedas respectivamente.

JUEGOS: La forma de ganar monedas o perder monedas depende del juego:

- Juego de la ruleta: las monedas se apuestan en una ruleta francesa de casino (con solo un 0). Esta ruleta admite apuestas de rojo-negro, par-impar, mitades, tercios, filas y números individuales. 
El juego solo dura una tirada, por lo que tras cada tirada se repartirá un premio.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Juego de la democracia: los jugadores se dividen en dos equipos de colores de forma aleatoria. Si los jugadores son impares un equipo tendrá un jugador menos, pero esto no tiene que ser necesariamente malo para ese equipo.

  El suelo es una cuadrícula de cuadrados de los dos colores, repartidos de manera aleatoria. Todos los jugadores de la partida controlarán al mismo personaje, que solo podrá estar en una casilla a la vez. El objetivo de los jugadores es hacer que el personaje se mantenga el máximo tiempo posible en las casillas del color de su equipo. El juego dura 30 segundos, y el personaje se moverá una vez por segundo. El movimiento será la suma de fuerzas de la decisión democrática emitida entre todos los jugadores de ambos equipos. Cada jugador tendrá 1 click cada segundo para decidir hacia qué dirección mover el personaje, pudiendo abstenerse a moverlo. El equipo ganador es aquel que mantenga al personaje en su color más segundos que el rival, pudiendo empatar.

  Al terminar el juego los jugadores del equipo ganador ganarán 5 monedas por cada segundo del resultado de la resta entre su tiempo menos el del equipo rival. Nadie pierde monedas, de manera que es un juego de recuperación de monedas.
  
--------------------------------------------------------------------------------------------------------------------------------------------------------------------

El año que viene estarán disponibles:

- Juego del ahorcado: es una adaptación del juego tradicional del ahorcado donde los jugadores van a colaborar y competir para adivinar la misma frase. Se adivinan frases y no palabras para que sea más largo y difícil al haber muchos jugadores, al estilo de La Ruleta de la Suerte. En el juego tradicional se acerca la horca si el jugador dice una letra que no está en la palabra. En este caso será diferente, y se acercará la horca para todo el grupo si más de 1/4 de los jugadores dice una letra que no está en la frase. Las frases estarán generadas por ChatGPT, y todas serán oraciones en tono de broma/hipérbole de entre 10 y 12 palabras, pudiendo pedirle que haya muchas apariciones de una cierta letra poco común para hacerlo más interesante y los nombres de algunos jugadores como protagonistas.
  
  El juego dura hasta que se adivine una frase entera o que acaben los turnos del ahorcado. El juego está compuesto de pasos donde los jugadores dirán cada uno una letra. El jugador o los jugadores que hayan elegido la letra que más veces aparece en la frase entre las votadas en un cierto paso se reparten las monedas de las veces que aparezca y esa será la letra que se hará pública. En el caso de empate entre varias se revelan todas ellas. Cada letra encontrada equivale a 10 monedas, por lo que este premio se reparte equitativamente entre todos los que la hayan dicho, redondeando a la alza. De esta manera se recompensa a los jugadores que digan una letra arriesgada que esté muy repetida, ya que se quedarían el premio para ellos solos. Los jugadores que hayan elegido otras letras distintas a la ganadora no sabrán si su letra estaba en la palabra, como mucho sabrán que estaba menos repetida que la seleccionada y si se ha acercado la horca pueden pensar que es porque no estaba la suya. Existe la posibilidad de que los jugadores puedan escribir la frase entera en vez de una letra. Aquellos jugadores que la acierten se repartirán el premio acumulado en el bote, que va bajando en 5 monedas cada turno. Si alguien intenta adivinar la frase y se equivoca pierde 10 monedas y queda eliminado.

  El final del juego llega cuando o se ha adivinado la frase o se han agotado las 5 vidas para que llegue la horca. Si agotan las vidas de la horca las palabras que queden por revelar serán repartidas entre algunos de los jugadores para que intenten acertar la frase entre todos y librarse del castigo. Si alguno falla, todos serán ahorcados, y todos los jugadores perderán 5 monedas por cada letra que hayan fallado durante la partida. De esta manera acertar la frase entre todos beneficia a aquellos jugadores menos afortunados con las letras, ya que no tendrían castigo. Si alguno de los ahorcados no tiene tantas monedas como las que debe perder, se queda a 0.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Juego de las tragaperras secretas: se crean tantas tragaperras como jugadores, cada una con una probabilidad aleatoria entre 0.2 y 0.8 de dar premios, y una propiedad multiplicativa de la cantidad de premio (duplicar, triplicar o cuadruplicar la apuesta) asignada aleatoriamente de forma equiprobable. Ambas propiedades son secretas a todos los jugadores y se revelarán al final del juego. Los jugadores solo concerán el valor multiplicativo de las máquinas a las que apuesten si ganan a ellas fijándose en la cantidad de monedas que reciben.

  Un juego son 7 apuestas de todos los jugadores, y en cada una se pide a cada jugador que apueste las monedas que quiera a una de ellas. Después de que todos apuesten cada jugador verá en su móvil cuánto dinero ha ganado su apuesta, y en la tele a qué tragaperras han apostado los demás en esa ocasión. Además, también aparecerá a modo de recordatorio cuántas personas han apostado a cada máquina a lo largo del juego. De esta manera los jugadores se fijarán en qué personas repiten las apuestas a la misma máquina y qué máquinas son las más populares y podrán decidir si cambian a esa.

- Juego de los saludos: a cada jugador se le asignan varios otros jugadores a los que debe saludar y el objetivo es que se cruce con todos en un mapa laberíntico, utilizando los controles de cruceta habituales de los videojuegos. Algunos de esos jugadores también querrán saludarle a él, pero otros no, por lo que el juego es una mezcla entre un juego de saludos voluntarios e involuntarios (pilla-pilla). Gana el primer jugador que salude a todos los de su lista. Por cada jugador saludado, se ganan 3 monedas. El ganador se lleva 30 monedas extra.

  Para que el juego sea completamente justo, la inicialización del mismo debe cumplir varios requisitos:
  - Cada jugador tiene en su lista a N otros jugadores (a los que debe pillar o saludar voluntariamente): garantiza que todos tengan el mismo número de tareas de buscar jugadores.
  - Cada jugador aparece en la lista de otros N jugadores: garantiza que todos tengan el mismo número de tareas de ser buscados.
  
  Sin embargo, estas dos condiciones no bastan para que sea justo: si se asignan las listas aleatoriamente puede ocurrir que haya algún jugador que tenga que saludar a muchos jugadores que no quieren saludarle, mientras que otros no tengan que saludar a nadie que no quiera saludarle. Para evitar esto, se añade la siguiente condición:
  - Todos los jugadores deben realizar M saludos voluntarios (el otro jugador también quiere saludarle): garantiza que las características de los saludos que realizan estén en igualdad de condiciones. Cada jugador debe pillar a |jugadores| - M jugadores y saludar voluntariamente a M jugadores.
  
  La inicialización del juego consiste en crear un grafo dirigido de jugadores donde cada uno tenga N aristas de entrada y N aristas de salida, y que M de ellas sean bidireccionales (2 aristas de tipos distintos forman una). Se prueban experimentalmente varios valores de N y M para quedarse con el grafo más balanceado posible en cuanto a número de inputs, outputs y bidireccionales. El algoritmo es completamente determinista, dependiendo únicamente en el |jugadores|.

AGRADECIMIENTOS (de Guille): 
- A Toña por ayudar con la programación, ideas y apoyo moral.
- A Florin por realizar el diseño de la mayoría de pantallas con temática navideña (y pese a eso no haber jugado).
- A Carmen por hacer ilustraciones que tristemente no pudieron ser incluídas, pero que serán tenidas en cuenta para el año que viene.
- A Toña y a Juanda por aguantar mis fantasías sobre los juegos.

EDICIÓN 2O22: Jugamos Toña, Juanda, Carmen, Sonia, Pablo, Marcos IA, Marcos Chelo, Nayla y Guille. Fue divertido, pero se hizo tedioso por deadlocks en el login y petadas después de jugar al juego de la democracia que hacía que hubiera que reiniciar la partida y como no había base de datos había que reiniciar las monedas, hay que crear una que lleve todos los datos de la partida por su hubiera problemas. Se hizo tedioso que había demasiada probabilidad de que tocara dulce (40%), el año que viene se bajará al 25%. Además, los usuarios de iPhone no veían bien los controles del juego de la democracia. Todo esto se debió a las prisas del desarrollo y no haber testeado la partida con muchas personas como estaba planeado, el año que viene debe hacerse así. A nivel de arquitectura web, es necesario incluirle sockets en vez de hacer polling. Sería conveniente configurar un servidor DNS para crear un dominio para la página.
