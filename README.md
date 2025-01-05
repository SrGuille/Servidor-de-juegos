# Servidor-de-juegos
Este es un proyecto de un servidor de videojuegos pensado para pasar un buen rato con amigos en Navidad.

CONDICIONES PREVIAS: Se recomienda ser entre 8 y 15 personas. Para participar todos deben traer 3 regalos de precios ascendentes, llamados regalo pequeño, mediano y grande.

SERVIDOR: El juego discurrirá en una red local. Idealmente el ordenador que haga de servidor deberá ser conectado a un televisor que todos puedan ver para mostrar los escenarios de los juegos. Ese ordenador además realizará la labor de administrador del juego.

JUGADORES: Cada jugador se conectará desde su móvil al servidor y participará en los juegos utilizando controles sencillos, con el objetivo de conseguir monedas. Todos comienzan con 200 monedas.

DINÁMICA: Durante todo el tiempo de juego todos los jugadores juegan a uno de los juegos y después se reparte un premio a uno de ellos. El administrador elegirá qué juegos ocurrirán a continuación, pudiendo elegir que un juego se repita varias veces seguidas o elegir que ocurran varias rondas de juegos aleatorios (siempre con premios entre partidas). La única excepción ocurre cuando algún jugador o jugadores se quedan sin monedas tras un juego o premio, en cuyo caso ocurrirá obligatoriamente un juego gratuito (democracia o ahorcado), donde no hacen falta monedas para jugar. Si tras ese juego alguno de los arruinados no ha ganado nada, se le darán 10 monedas gratis.

PREMIOS/ECONOMÍA: El ganador del premio no es el ganador del juego, sino que se utiliza una ruleta con los nombres de los participantes. Esta es dinámica, ya que la probabilidad de ganar de cada uno depende directamente de las monedas que tenga en comparación con los demás. El premio que se llevará puede ser cualquiera de los 3 tipos de regalos, decidiéndose esto también mediante otra ruleta que les da la misma probabilidad. El ganador canjeará su regalo por monedas, para dejar espacio a que los otros jugadores ganen en las siguientes ocasiones. Los regalos cuestan un porcentaje de sus monedas: el costará 10%, el 15% el 20% respectivamente. El juego está regulado para que no haya inflación, al final de cada ronda -tras repartir el regalo- se calcula si se ha producido inflación o deflación. En el primer caso, se hacen desaparecer monedas de los jugadores más ricos y con más regalos siguiendo una fórmula. En caso contrario -lo que es lo más común- se reparten esas monedas faltantes entre los jugadores más pobres con una fórmula que tiene en cuenta sus monedas, regalos y las monedas que acaba de ganar (a modo de boost). Cuando la partida está avanzada puede ocurrir que santa le regale un regalo al jugador más pobre o que ocurra un duelo al mejor de 3 del pistolero si un jugador muy rico gana otro regalo entre él y el más pobre para robárselo.

JUEGOS: La forma de ganar monedas o perder monedas depende del juego:

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Juego de la ruleta:
  
  Las monedas se apuestan en una ruleta francesa de casino (con solo un 0). Esta ruleta admite apuestas de rojo-negro, par-impar, mitades, tercios, filas y números individuales. 

  El juego solo dura una tirada, por lo que tras cada tirada se repartirá un premio.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Juego de la democracia:

  Los jugadores se dividen en dos equipos de colores de forma aleatoria. Si los jugadores son impares un equipo tendrá un jugador menos, pero esto no tiene que ser necesariamente malo para ese equipo.

  El suelo es una cuadrícula de cuadrados de los dos colores de 19x19 casillas, repartidos de manera aleatoria. Todos los jugadores de la partida controlarán al mismo personaje, que solo podrá estar en una casilla a la vez. El objetivo de los jugadores es hacer que el personaje se mantenga el máximo tiempo posible en las casillas del color de su equipo. El juego dura 30 segundos, y el personaje se moverá una vez por segundo. El movimiento será la suma de fuerzas de la decisión democrática emitida entre todos los jugadores de ambos equipos. Se divide entre dos la fuerza total para evitar que el personaje se mueva demasiado. Cada jugador tendrá 1 click cada segundo para decidir hacia qué dirección mover el personaje, pudiendo abstenerse a moverlo. El equipo ganador es aquel que mantenga al personaje en su color más segundos que el rival, pudiendo empatar.

  Al terminar el juego cada jugador del equipo ganador le roba 5 monedas a un jugador del equipo perdedor por cada casilla extra que haya pasado el personaje en su color. En el caso de ser impares se gestiona de manera más compleja para repartir bien las monedas entre los equipos.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Juego de los números ciegos:

  Inspirado en el juego https://blindnumber.com/, que consiste en tener que ordenar en una lista 10 números aleatorios del 0 al 999, que te son revelados de uno. Cuando te dicen un número tienes que colocarlo en su posición definitiva de tu lista, siempre con el riesgo de fallar, ya que no conoces los siguientes. Si en un paso ya no puedes colocar el número en la lista, pierdes.
  
  El juego es una extensión de esta idea formando 2 equipos de jugadores, cada uno jugando el juego en paralelo a pantalla partida con números distintos. Solo es necesario que uno de los jugadores del equipo interactúe con el juego, se decide aleatoriamente quien puede y se avisa a los demás que vayan con él. La partida dura 1.5 minutos, y gana el equipo que al llegar el fin del tiempo tenga más números colocados. Es válido que los equipos pierdan todas las veces que quieran durante la partida, lo que causa que se les reinicie su lista de nuevo. La gracia del juego está en decidir si el equipo se planta o no. El premio para cada jugador es de 5 monedas por cada número de ventaja, y en caso de empate no se reparte nada. En caso de que un equipo gane se acaba el juego como se haya quedado.

  En el móvil ves las posiciones disponibles en las que puedes poner y en la tele se ve la lista actual y el nuevo número de los dos equipos.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Pistolero rey de la pista:

  Se trata del popular juego de niños pistolero, en el cual se enfrentan dos jugadores a un duelo de disparos. Los dos empiezan sin balas y tienen 3 movimientos posibles: disparar 1 bala (si tienen), recargar o protegerse. Pueden acumular tantas balas como puedan recargar. Si ambos se disparan a la vez los dos mueren. Mi adaptación incluye el recurso de los escudos para hacerlo más dinámico. Cuando empieza un duelo los dos jugadores tienen una bala y dos escudos, y recargar les da uno de cada. El jugador que gana se queda en la pista y se enfrenta al siguiente, manteniendo las balas y escudos de la partida anterior (o siendo inicializados a 1 y 2 si tenía menos).

  Si ganas un duelo le robas 10 monedas al perdedor. La partida dura 1 vuelta entera por todos los jugadores. Si el último jugador se queda sin rival se elige uno aleatoriamente entre los demás.

  En el móvil ves tus balas, escudos y los 3 botones. En la pantalla los datos de los jugadores enfrentados y luego una animación y sonidos con la decisión de cada uno. 

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

El año que viene:

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Juego de las tragaperras secretas:

  Se crean tantas 5 tragaperras y todos los jugadores apostarán la cantidad de monedas que deseen a una de ellas durante 5 turnos diferentes. Se trata de un juego exploración vs explotación donde los jugadores deberán descubrir la mejor tragaperras. Cada máquina tiene una probabilidad de dar premio secreta -que se revela al final-. que se define como un rango multiplicativo aleatorio (por ejemplo, una de ellas [x0.6 a x1.7]) y cuando se apuesta a ellas se decide aleatoriamente en qué punto del intervalo cae (e.g. x0.9, lo que haría perder el 10% de las monedas apostadas). Estas máquinas deben ser inicializadas con diferentes amplitudes y centros de rango. Cuando un jugador apuesta a una se le revelará qué premio que se ha llevado. También sabrá qué están haciendo los demás para decidir si te cambia a la próxima: a qué máquina está apostando cada jugador en cada turno y cuántos han apostado a cada una de manera histórica.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Juego de los saludos:

  A cada jugador se le asignan varios otros jugadores a los que debe saludar y el objetivo es que se cruce con todos en un mapa laberíntico 2D bastante grande, utilizando los controles de cruceta habituales de los videojuegos. Los jugadores están representados por formas y colores únicos. Se puede correr a una velocidad máxima no muy rápida. Algunos de esos jugadores también querrán saludarle a él, pero otros no, por lo que el juego es una mezcla entre un juego de saludos voluntarios e involuntarios (pilla-pilla). La gracia del juego son los momentos de amistad y enemistad que se dan en el recorrido, porque tú sabes a quien quieres cruzarte, pero no si ellos quieren saludarte o no y tampoco quien te quiere pillar a ti. Gana el primer jugador que se cruce con todos los de su lista. Por cada jugador cruzado, se ganan 3 monedas. El ganador se lleva 30 monedas extra.

  Para que el juego sea completamente justo, la inicialización del mismo debe cumplir varios requisitos:
  - Cada jugador tiene en su lista a N otros jugadores (con los que debe cruzarse, ya sea pillarles o saludarles voluntariamente): garantiza que todos tengan el mismo número de tareas de buscar jugadores.
  - Cada jugador aparece en la lista de otros N jugadores: garantiza que todos tengan el mismo número de tareas de ser buscados.
  
  Sin embargo, estas dos condiciones no bastan para que sea justo: si se asignan las listas aleatoriamente puede ocurrir que haya algún jugador que tenga que saludar a muchos jugadores que no quieren saludarle (difícil para él), mientras que otros no tengan que saludar a nadie que no quiera saludarle (fácil para él). Para evitar esto, se añade la siguiente condición:
  - Todos los jugadores deben realizar M saludos voluntarios (el otro jugador también quiere saludarle): garantiza que las características de los saludos que realizan estén en igualdad de condiciones. Cada jugador debe pillar a (N - M) jugadores y saludar voluntariamente a M jugadores.
  
  La inicialización del juego consiste en crear un grafo dirigido de jugadores donde cada uno tenga N aristas de entrada (deben cruzarse con él) y N aristas de salida (debe cruzarse con ellos), y que M de ellas sean bidireccionales (2 aristas de tipos distintos forman una). No existen grafos para todas las combinaciones de N y M, por lo que se prueban experimentalmente varios valores de N y M para quedarse con el grafo más balanceado posible en cuanto a número de inputs, outputs y bidireccionales. El algoritmo es completamente determinista, dependiendo únicamente en el |jugadores|.

  Cada vez que dos jugadores se saludan, se reproduce una música feliz y cada vez que alguien pilla a alguien se reproduce un sonido de lucha. Cada uno ve en su pantalla la lista de a quien debe pillar. Cuando ya ha pillado a alguien le desaparece para no confundir.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Juego del panel secreto:

  Las frases están generadas por ChatGPT, y todas serán oraciones en tono de broma/hipérbole de entre 10 y 12 palabras, pudiendo pedirle que haya muchas apariciones de una cierta letra poco común para hacerlo más interesante y los nombres y aficiones de uno de los jugadores como protagonista. El servidor revelará una letra de la frase cada dos segundos y el juego se convierte en una carrera por enviar palabras enteras de la frase. Si eres el primero en acertarla, te llevas monedas (en base a las letras no reveladas que has acertado), y si envías una palabra fallida pierdes monedas. Se puede enviar más de una palabra a la vez siempre que se separen con espacios. Cuando un jugador acierta una palabra se revela entera para los demás.

  Este modifica el juego del ahorcado que no funcionaba por ser demasiado complejo, tedioso y raro a nivel matemático a la hora de repartir los premios.
  
--------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Juego del cronómetro
  
  El juego trata de adivinar cuánto tiempo ha pasado. Se decide un cierto tiempo aleatorio (entre 1 y 20 segundos) y los jugadores deberán pulsar un botón prediciendo cuándo ha pasado ese tiempo. Se hará 3 veces seguidas y se irán eliminando a los peores jugadores (o quizás dejar pasar solo a los x mejores). Se mostrará en pantalla una recta con los tiempos de todos los jugadores. Los que pasan de ronda se llevan monedas de los eliminados. La principal desventaja de este juego es que es demasiado simple y podría ser sustituido por otra acción rápida más compleja manteniendo el sistema de eliminación.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

AGRADECIMIENTOS (de Guille): 
- A Toña por ocuparse de la organización de los eventos y ayudar con la programación el primer año.
- A Florin por realizar el diseño de la mayoría de pantallas con temática navideña.
- A Toña y a Juanda por aguantar recurrentemente mis fantasías sobre los juegos.
- A todos por sus ideas y comentarios.

EDICIÓN 2O22: Jugamos Toña, Juanda, Carmen, Sonia, Pablo, Marcos IA, Marcos Chelo, Nayla y Guille. Fue divertido, pero se hizo tedioso por deadlocks en el login y petadas después de jugar al juego de la democracia que hacía que hubiera que reiniciar la partida y como no había base de datos había que reiniciar las monedas, hay que crear una que lleve todos los datos de la partida por su hubiera problemas. Se hizo tedioso que había demasiada probabilidad de que tocara dulce (40%), el año que viene se bajará al 25%. Además, los usuarios de iPhone no veían bien los controles del juego de la democracia. Todo esto se debió a las prisas del desarrollo y no haber testeado la partida con muchas personas como estaba planeado, el año que viene debe hacerse así. A nivel de arquitectura web, es necesario incluirle sockets en vez de hacer polling. Sería conveniente configurar un servidor DNS para crear un dominio para la página.

EDICIÓN 2O23: Jugamos Toña, Juanda, Carmen, Jaime, Sonia, Cosmin, Marcos IA, Marcos Chelo, Florin, Patri, Nayla y Guille. Fue mejor que el año anterior por la solución de los bugs en el login, la calidad del sistema de sockets y por la tranquilidad que daba la base de datos por no perder la partida. Hubo algunos problemas con personas que se equivocaban de nombre en la lista al hacer el login, hay que implementar que una vez te loguees la primera vez no tener la opción de elegir tu nombre de la lista para que no te puedas equivocar. Se balanceó la probabilidad de dulce a 25% y el juego se hizo más satisfactorio. El año anterior en el juego de la democracia daba mucha sensación de que el muñeco se teletransportaba por el terreno y este mejoró mucho ampliando el terreno y haciendo que fuerza se dividiera entre 2 para que el muñeco no se moviera tanto. Hay que pensar cómo balancear los juegos colaborativos dependiendo del número de jugadores, por ejemplo, puede que la medida aplicada al de la democracia no funcione si somos menos. La primera vez que jugamos al de la democracia le hicimos un DoS involuntario al servidor porque se spameó mucho a los botones. Ya no pasó más porque advertí a la gente que spammear no servía y que solo se regista una pulsación por segundo y spammearon menos. El año que viene hay que hacer que se pueda spammear lo que se quiera pero que no se envíe más que 1 por segundo al servidor. Los problemas serios vinieron del lado del juego del ahorcado que tuvo que modificarse en directo para repararlo. Lo peor fue que las frases que generaba el ChatGPT no tenían mucho sentido por las restricciones que le puse y se hacían imposibles de adivinar. Además, hay que hacer que la parte de la frase que ya está adivinada se compie automáticamente al móvil y que cuando falles puedas ver la frase que habías puesto para modificarla ligeramente. Además, había un bug que daba excepción cuando terminaba la partida y no se adivinaba la frase por no contar bien el número de pasos. Hay que pensar siene sentido hacer algún tipo de balanceo en la economía del juego para intentar hacer más justo el reparto de regalos y evitar que alguien se quede sin monedas o con pocas. Posiblemente la estrategia sea penalizar que te hayas quedado sin monedas unas cuentas rondas (p.e., 5 rondas), pero luego regalar bastantes para que puedas remontar, por ejemplo dándote 100 monedas de repente. Sería divertido implementarlo con la imagen del Karl Marx de Navidad, que salga el mensaje de que se te ha rescatado.

EDICIÓN 2024: Jugamos Toña, Juanda, Marcos PSOE, Marcos Masón, Rafa, Diego Hippie, Ainara, Sonia, Diego Tatus, Ana, Nayla, Isa, Cris, Guillermo y yo (doble Guillermo). Ha sido el mejor año con diferencia por la cantidad de juegos y lo pulidos que estaban (aunque ha habido algunos bugs). La regulación ha sido un acierto y el juego del pistolero ha sido el más aclamado. El ahorcado fue eliminado por sus problemas teóricos, pero no se ha echado en falta. He apuntado estas mejoras:
- Ruleta: comprobar todas las apuestas, ya que parece haber bugs en algunas.
- Pistolero: arreglar bug escudos negativos, pensar en si meter rachas de victorias que impliquen ganar más monedas.
- Blind number: ha sido el juego que peor ha funcionado, tanto por los bugs de JS (y puede que del servidor) como por el balanceo. Hay que intentar desincentivar que ocurran empates ya que le quita la gracia. Para ello bajar a 8 casillas la lista para que sea más fácil ganar y subir premio a 50 monedas si se gana entero (+ quizás casillas de ventaja). También poner 3 o 4 equipos para que no haya tanta gente en cada uno y añadir caos. Si hay empate al final hacer checkpoint y que los equipos empatados terminen la partida.
- Regulación: tener en cuenta el tipo de regalo en la richness score y no penalizar tanto por regalo (quizás 80 en vez de 100)
- Probar santa y duelo especial.
- Hacer el rework del ahorcado -> panel secreto (mejorar prompt).
- Hacer el código más seguro: poner muchos try catch y repasar estabilidad de las queries (especialmente coins y prizes evolution)
