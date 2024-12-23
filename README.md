# Servidor-de-juegos
Este es un proyecto de un servidor de videojuegos pensado para pasar un buen rato con amigos en Navidad.

CONDICIONES PREVIAS: Se recomienda ser entre 5 y 15 personas. Para participar todos deben traer 3 regalos de precios ascendentes, llamados regalo pequeño, mediano y grande.

SERVIDOR: El juego discurrirá en una red local. Idealmente el ordenador que haga de servidor deberá ser conectado a un televisor que todos puedan ver para mostrar los escenarios de los juegos. Ese ordenador además realizará la labor de administrador del juego.

JUGADORES: Cada jugador se conectará desde su móvil al servidor y participará en los juegos utilizando controles sencillos, con el objetivo de conseguir monedas. Todos comienzan con 200 monedas.

DINÁMICA: Durante todo el tiempo de juego todos los jugadores juegan a uno de los juegos y después se reparte un premio a uno de ellos. El administrador elegirá qué juegos ocurrirán a continuación, pudiendo elegir que un juego se repita varias veces seguidas o elegir que ocurran varias rondas de juegos aleatorios (siempre con premios entre partidas). La única excepción ocurre cuando algún jugador o jugadores se quedan sin monedas tras un juego o premio, en cuyo caso ocurrirá obligatoriamente un juego gratuito (democracia o ahorcado), donde no hacen falta monedas para jugar. Si tras ese juego alguno de los arruinados no ha ganado nada, se le darán 10 monedas gratis.

PREMIOS/ECONOMÍA: El ganador del premio no es el ganador del juego, sino que se utiliza una ruleta con los nombres de los participantes. Esta es dinámica, ya que la probabilidad de ganar de cada uno depende directamente de las monedas que tenga en comparación con los demás. El premio que se llevará puede ser un dulce o un regalo pequeño, mediano o grande, decidiéndose esto también mediante otra ruleta. El ganador canjeará su regalo por monedas, para dejar espacio a que los otros jugadores ganen en las siguientes ocasiones. Si ha ganado un dulce, le costará 5 monedas. Si ha ganado un regalo, le costará 20, 30 o 40 monedas respectivamente.

JUEGOS: La forma de ganar monedas o perder monedas depende del juego:

- Juego de la ruleta:
  
  Las monedas se apuestan en una ruleta francesa de casino (con solo un 0). Esta ruleta admite apuestas de rojo-negro, par-impar, mitades, tercios, filas y números individuales. 

  El juego solo dura una tirada, por lo que tras cada tirada se repartirá un premio.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Juego de la democracia:

  Los jugadores se dividen en dos equipos de colores de forma aleatoria. Si los jugadores son impares un equipo tendrá un jugador menos, pero esto no tiene que ser necesariamente malo para ese equipo.

  El suelo es una cuadrícula de cuadrados de los dos colores, repartidos de manera aleatoria. Todos los jugadores de la partida controlarán al mismo personaje, que solo podrá estar en una casilla a la vez. El objetivo de los jugadores es hacer que el personaje se mantenga el máximo tiempo posible en las casillas del color de su equipo. El juego dura 30 segundos, y el personaje se moverá una vez por segundo. El movimiento será la suma de fuerzas de la decisión democrática emitida entre todos los jugadores de ambos equipos. Cada jugador tendrá 1 click cada segundo para decidir hacia qué dirección mover el personaje, pudiendo abstenerse a moverlo. El equipo ganador es aquel que mantenga al personaje en su color más segundos que el rival, pudiendo empatar.

  Al terminar el juego los jugadores del equipo ganador ganarán 5 monedas por cada segundo del resultado de la resta entre su tiempo menos el del equipo rival. Nadie pierde monedas, de manera que es un juego de recuperación de monedas.
  
--------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Juego del ahorcado:

  Es una adaptación del juego tradicional del ahorcado donde los jugadores van a colaborar y competir para adivinar la misma frase. Se adivinan frases y no palabras para que sea más largo y difícil al haber muchos jugadores, al estilo de La Ruleta de la Suerte. En el juego tradicional se acerca la horca si el jugador dice una letra que no está en la palabra. En este caso será diferente, y se acercará la horca para todo el grupo si más de 1/4 de los jugadores dice una letra que no está en la frase. Las frases están generadas por ChatGPT, y todas serán oraciones en tono de broma/hipérbole de entre 10 y 12 palabras, pudiendo pedirle que haya muchas apariciones de una cierta letra poco común para hacerlo más interesante y los nombres y aficiones de 1 o 2 de los jugadores como protagonistas.

  El juego dura hasta que se adivine una frase entera o que acaben los turnos del ahorcado. El juego está compuesto de pasos donde los jugadores dirán cada uno una letra. El jugador o los jugadores que hayan elegido la letra que más veces aparece en la frase entre las votadas en un cierto paso se reparten las monedas de las veces que aparezca y esa será la letra que se hará pública. En el caso de empate entre varias se revelan todas ellas. Cada letra encontrada equivale a 10 monedas, por lo que este premio se reparte equitativamente entre todos los que la hayan dicho, redondeando a la alza. De esta manera se recompensa a los jugadores que digan una letra arriesgada que esté muy repetida, ya que se quedarían el premio para ellos solos. Los jugadores que hayan elegido otras letras distintas a la ganadora no sabrán si su letra estaba en la palabra, como mucho sabrán que estaba menos repetida que la seleccionada y si se ha acercado la horca pueden pensar que es porque no estaba la suya. Existe la posibilidad de que los jugadores puedan escribir la frase entera en vez de una letra. Aquellos jugadores que la acierten se repartirán el premio acumulado en el bote, que va bajando en 5 monedas cada turno. Si alguien intenta adivinar la frase y se equivoca pierde 10 monedas y queda eliminado.

  El final del juego llega cuando o se ha adivinado la frase o se han agotado las 5 vidas para que llegue la horca. 

  POSIBLE MODIFICACIÓN: Si agotan las vidas de la horca las palabras que queden por revelar serán repartidas entre algunos de los jugadores para que intenten acertar la frase entre todos y librarse del castigo. Si alguno falla, todos serán ahorcados, y todos los jugadores perderán 5 monedas por cada letra que hayan fallado durante la partida. De esta manera acertar la frase entre todos beneficia a aquellos jugadores menos afortunados con las letras, ya que no tendrían castigo. Si alguno de los ahorcados no tiene tantas monedas como las que debe perder, se queda a 0.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

El año que viene:

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Juego de las tragaperras secretas:

  Se crean tantas tragaperras como jugadores, cada una con una probabilidad aleatoria en [0.2, 0.8] de dar premios, y una propiedad multiplicativa de la cantidad de premio (x2, x3 o x4) la apuesta asignada aleatoriamente de forma equiprobable. Ambas propiedades son secretas a todos los jugadores y se revelarán al final del juego. Los jugadores solo conocerán el valor multiplicativo de las máquinas a las que apuesten si ganan a ellas fijándose en la cantidad de monedas que reciben.

  Un juego son 7 apuestas de todos los jugadores, y en cada una se pide a cada jugador que apueste las monedas que quiera a una de ellas. Después de que todos apuesten cada jugador verá en su móvil cuánto dinero ha ganado su apuesta, y en la tele a qué tragaperras han apostado los demás en esa ocasión. Además, también aparecerá a modo de recordatorio cuántas personas han apostado a cada máquina a lo largo del juego. De esta manera los jugadores se fijarán en qué personas repiten las apuestas a la misma máquina y qué máquinas son las más populares y podrán decidir si cambian a esa.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Juego de los saludos:

  A cada jugador se le asignan varios otros jugadores a los que debe saludar y el objetivo es que se cruce con todos en un mapa laberíntico 2D bastante grande, utilizando los controles de cruceta habituales de los videojuegos. Se puede correr a una velocidad máxima no muy rápida. Algunos de esos jugadores también querrán saludarle a él, pero otros no, por lo que el juego es una mezcla entre un juego de saludos voluntarios e involuntarios (pilla-pilla). La gracia del juego son los momentos de amistad y enemistad que se dan en el recorrido, porque tú sabes a quien quieres cruzarte, pero no si ellos quieren saludarte o no y tampoco quien te quiere pillar a ti. Gana el primer jugador que se cruce con todos los de su lista. Por cada jugador cruzado, se ganan 3 monedas. El ganador se lleva 30 monedas extra.

  Para que el juego sea completamente justo, la inicialización del mismo debe cumplir varios requisitos:
  - Cada jugador tiene en su lista a N otros jugadores (con los que debe cruzarse, ya sea pillarles o saludarles voluntariamente): garantiza que todos tengan el mismo número de tareas de buscar jugadores.
  - Cada jugador aparece en la lista de otros N jugadores: garantiza que todos tengan el mismo número de tareas de ser buscados.
  
  Sin embargo, estas dos condiciones no bastan para que sea justo: si se asignan las listas aleatoriamente puede ocurrir que haya algún jugador que tenga que saludar a muchos jugadores que no quieren saludarle (difícil para él), mientras que otros no tengan que saludar a nadie que no quiera saludarle (fácil para él). Para evitar esto, se añade la siguiente condición:
  - Todos los jugadores deben realizar M saludos voluntarios (el otro jugador también quiere saludarle): garantiza que las características de los saludos que realizan estén en igualdad de condiciones. Cada jugador debe pillar a (N - M) jugadores y saludar voluntariamente a M jugadores.
  
  La inicialización del juego consiste en crear un grafo dirigido de jugadores donde cada uno tenga N aristas de entrada (deben cruzarse con él) y N aristas de salida (debe cruzarse con ellos), y que M de ellas sean bidireccionales (2 aristas de tipos distintos forman una). No existen grafos para todas las combinaciones de N y M, por lo que se prueban experimentalmente varios valores de N y M para quedarse con el grafo más balanceado posible en cuanto a número de inputs, outputs y bidireccionales. El algoritmo es completamente determinista, dependiendo únicamente en el |jugadores|.

  Cada vez que dos jugadores se saludan, se reproduce una música feliz y cada vez que alguien pilla a alguien se reproduce un sonido de lucha. Cada uno ve en su pantalla la lista de a quien debe pillar. Cuando ya ha pillado a alguien le desaparece para no confundir.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Juego de los números ciegos:

  Inspirado en el juego https://blindnumber.com/, que consiste en tener que ordenar en una lista 10 números aleatorios del 0 al 999, que te son revelados de uno. Cuando te dicen un número tienes que colocarlo en su posición definitiva de tu lista, siempre con el riesgo de fallar, ya que no conoces los siguientes. Si en un paso ya no puedes colocar el número en la lista, pierdes.
  
  Se va a extender esta idea formando 2 equipos de jugadores, cada uno jugando el juego en paralelo a pantalla partida con números distintos. Solo es necesario que uno de los jugadores del equipo interactúe con el juego, se decidirá aleatoriamente quien puede. La partida durará 2 minutos, y gana el equipo que al llegar el fin del tiempo tenga más números colocados. Es válido que los equipos pierdan todas las veces que quieran durante la partida, lo que causa que se les reinicie su lista de nuevo. La gracia del juego está en decidir si el equipo se planta o no. El premio para cada jugador es 2 * cantidad de números que hayan colocado en la lista. En el caso de empate, se reparte el premio entre los dos equipos. La interfaz gráfica va a ser muy similar a la del juego original y será clonada en los móviles y en la pantalla principal.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Pistolero rey de la pista:

  Se trata del popular juego de niños pistolero, en el cual se enfrentan dos jugadores a un duelo de disparos. Los dos empiezan sin balas y tienen 3 movimientos posibles: disparar 1 bala (si tienen), recargar o protegerse. Pueden acumular tantas balas como puedan recargar. Si ambos se disparan a la vez no gana ninguno (decidir si sigue la partida o no, creo que sí). El jugador que gana se queda en la pista y se enfrenta al siguiente, manteniendo las balas de la partida anterior (o no, pero creo que sí, parece más divertido para que se vea como un rival a batir).

  Si ganas un duelo ganas monedas, si pierdes, pierdes monedas. Puede estar bien que haya multiplicadores por racha siendo el rey de la pista.

  Si hay demasiados jugadores puede hacerse pesado que no se juegue mucho. Debe ser dinámico, debe haber 3 segundos para decidir cada movimiento. Si no le das a tiempo se decide una acción aleatoria entre las posibles. La partida dura 1 vuelta entera por todos los jugadores. 

  En el móvil ves tus balas y los 3 botones. En la pantalla los nombres de los jugadores enfrentados y luego una animación con la decisión de cada uno. Cuando se cambie a otro jugador, el nuevo le dé a un botón de que está listo para que comience el duelo.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

AGRADECIMIENTOS (de Guille): 
- A Toña por ayudar con la programación, ideas y apoyo moral.
- A Florin por realizar el diseño de la mayoría de pantallas con temática navideña (y pese a eso no haber jugado).
- A Carmen por hacer ilustraciones que tristemente no pudieron ser incluídas, pero que serán tenidas en cuenta para el año que viene.
- A Toña y a Juanda por aguantar mis fantasías sobre los juegos.

EDICIÓN 2O22: Jugamos Toña, Juanda, Carmen, Sonia, Pablo, Marcos IA, Marcos Chelo, Nayla y Guille. Fue divertido, pero se hizo tedioso por deadlocks en el login y petadas después de jugar al juego de la democracia que hacía que hubiera que reiniciar la partida y como no había base de datos había que reiniciar las monedas, hay que crear una que lleve todos los datos de la partida por su hubiera problemas. Se hizo tedioso que había demasiada probabilidad de que tocara dulce (40%), el año que viene se bajará al 25%. Además, los usuarios de iPhone no veían bien los controles del juego de la democracia. Todo esto se debió a las prisas del desarrollo y no haber testeado la partida con muchas personas como estaba planeado, el año que viene debe hacerse así. A nivel de arquitectura web, es necesario incluirle sockets en vez de hacer polling. Sería conveniente configurar un servidor DNS para crear un dominio para la página.

EDICIÓN 2O23: Jugamos Toña, Juanda, Carmen, Jaime, Sonia, Cosmin, Marcos IA, Marcos Chelo, Florin, Patri, Nayla y Guille. Fue mejor que el año anterior por la solución de los bugs en el login, la calidad del sistema de sockets y por la tranquilidad que daba la base de datos por no perder la partida. Hubo algunos problemas con personas que se equivocaban de nombre en la lista al hacer el login, hay que implementar que una vez te loguees la primera vez no tener la opción de elegir tu nombre de la lista para que no te puedas equivocar. Se balanceó la probabilidad de dulce a 25% y el juego se hizo más satisfactorio. El año anterior en el juego de la democracia daba mucha sensación de que el muñeco se teletransportaba por el terreno y este mejoró mucho ampliando el terreno y haciendo que fuerza se dividiera entre 2 para que el muñeco no se moviera tanto. Hay que pensar cómo balancear los juegos colaborativos dependiendo del número de jugadores, por ejemplo, puede que la medida aplicada al de la democracia no funcione si somos menos. La primera vez que jugamos al de la democracia le hicimos un DoS involuntario al servidor porque se spameó mucho a los botones. Ya no pasó más porque advertí a la gente que spammear no servía y que solo se regista una pulsación por segundo y spammearon menos. El año que viene hay que hacer que se pueda spammear lo que se quiera pero que no se envíe más que 1 por segundo al servidor. Los problemas serios vinieron del lado del juego del ahorcado que tuvo que modificarse en directo para repararlo. Lo peor fue que las frases que generaba el ChatGPT no tenían mucho sentido por las restricciones que le puse y se hacían imposibles de adivinar. Además, hay que hacer que la parte de la frase que ya está adivinada se compie automáticamente al móvil y que cuando falles puedas ver la frase que habías puesto para modificarla ligeramente. Además, había un bug que daba excepción cuando terminaba la partida y no se adivinaba la frase por no contar bien el número de pasos. Hay que pensar siene sentido hacer algún tipo de balanceo en la economía del juego para intentar hacer más justo el reparto de regalos y evitar que alguien se quede sin monedas o con pocas. Posiblemente la estrategia sea penalizar que te hayas quedado sin monedas unas cuentas rondas (p.e., 5 rondas), pero luego regalar bastantes para que puedas remontar, por ejemplo dándote 100 monedas de repente. Sería divertido implementarlo con la imagen del Karl Marx de Navidad, que salga el mensaje de que se te ha rescatado.
