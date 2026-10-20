# Flare Curse: Implementacion vs Spec Original

Fecha de revision: 2026-04-08 (actualizada)

## 1. Resumen ejecutivo

Estado actual: Flare Curse esta implementado de extremo a extremo como juego server-authoritative, con cierre de partida, resumen final, audio host y cobertura de tests.

Incluye:
- Motor de juego con bucle periodico y lock global.
- Socket dedicado para acciones/eventos del juego.
- Pantalla de jugador y pantalla de host sin controles de gameplay.
- Integracion en selector de juegos y redireccionamiento admin/jugador.
- Historial de maldiciones + leaderboard de fantasmas en `FinJuego`.
- Resaltado visual de rebotes/aciertos en tabla final host.
- Musica host con Web Audio API (loops sincronizados y crossfade suave).
- Cola de voz host para anuncios de maldicion y cierre.
- Cobertura de tests de engine, protocolo socket y smoke multicliente.

No incluye todavia:
- Reproduccion local de loops en pantalla de jugador (el audio centralizado sigue en host).
- Limpieza opcional del campo `at_seconds` en payload de `curse_history` (se emite pero no se muestra en UI).

## 2. Cobertura por bloques de spec

## 2.1 Roles, equipos y condicion de fin

Spec:
- Dos equipos aleatorios ocultos.
- Si hay impar, un fantasma inicial.
- El juego termina cuando solo queda un equipo vivo.

Implementado:
- Asignacion aleatoria de equipos en inicializacion: `circle` y `square`.
- Si impar, se elige un jugador aleatorio como fantasma inicial con simbolo propio `ghost`.
- La condicion de fin se evalua por equipos vivos y se dispara al quedar uno.

Evidencia:
- servidor/games/flare_curse/flare_curse_engine.py:378
- servidor/games/flare_curse/flare_curse_engine.py:396
- servidor/games/flare_curse/flare_curse_engine.py:624

## 2.2 Flare de jugador vivo

Spec:
- Competicion por color disponible.
- Color retenible durante un tiempo.
- Al lanzar: se ilumina origen y un rival aleatorio.
- Si expira en mano, timeout y vuelve a cola prioritaria.

Implementado:
- `PedirDestello` reclama de forma exclusiva el color ofrecido.
- Al reclamar, se cierra la oferta con `DestelloNoDisponible`.
- Retencion de color: `HOLD_COLOR_SECONDS = 7.0`.
- `LanzarDestello` ilumina origen + objetivo rival aleatorio, y consume color.
- Timeout en mano detectado periodicamente y notificado con `TimeoutDestello`.

Evidencia:
- servidor/games/flare_curse/flare_curse_engine.py:189
- servidor/games/flare_curse/flare_curse_engine.py:208
- servidor/games/flare_curse/flare_curse_engine.py:445

## 2.3 Flare de fantasma

Spec:
- Fantasma tiene color propio permanente con cooldown.
- Si usa destello a tiempo (hay caras activas de su color), puede sumar punto.
- Debe elegir objetivo extra no involucrado en los ya iluminados de ese color.

Implementado:
- El color del fantasma se asigna desde ultimo color en cara, o aleatorio entre menos usados.
- Cooldown de fantasma: `GHOST_COOLDOWN_SECONDS = 9.0`.
- Contencion de llegada tardia configurable: `GHOST_POST_FACE_GRACE_SECONDS`.
- `LanzarDestelloFantasma` considera jugadores activos y, dentro de ventana de gracia, recien apagados.
- El objetivo fantasma se elige excluyendo ese conjunto de activadores; si no queda nadie, no tiene efecto.
- Suma punto solo si hay objetivo alternativo y la intervencion se considera valida.

Evidencia:
- servidor/games/flare_curse/flare_curse_engine.py:57
- servidor/games/flare_curse/flare_curse_engine.py:284
- servidor/games/flare_curse/flare_curse_engine.py:286
- servidor/games/flare_curse/flare_curse_engine.py:591
- servidor/games/flare_curse/flare_curse_engine.py:607
- servidor/games/flare_curse/test_flare_curse_engine.py:286
- servidor/games/flare_curse/test_flare_curse_engine.py:320
- servidor/games/flare_curse/test_flare_curse_engine.py:353

## 2.4 Maldicion (Curse)

Spec:
- Si maldices aliado, rebota y mueres tu.
- Si maldices rival, muere el rival.
- El maldito pasa a fantasma y se anuncia a todos.

Implementado:
- `cast_curse` aplica exactamente la regla aliado/rival.
- El maldito se convierte en fantasma con color asignado segun reglas.
- Se emite `NuevoJugadorMaldito` por broadcast.
- Si se cumple fin de partida, emite `FinJuego` y arranca cuenta atras final.
- Se guarda `curse_history` con origen, objetivo intentado, maldito final y resultado (`enemy_hit` / `self_rebound`).

Evidencia:
- servidor/games/flare_curse/flare_curse_engine.py:319
- servidor/games/flare_curse/flare_curse_engine.py:343
- servidor/games/flare_curse/flare_curse_engine.py:353
- servidor/games/flare_curse/flare_curse_engine.py:632
- servidor/games/flare_curse/flare_curse_engine.py:668

## 2.5 Liberacion de colores y concurrencia

Spec:
- Dos colas: timeouts (prioridad) y usados (con espera).
- Gap aleatorio entre liberaciones.
- Limite de colores simultaneos segun vivos.

Implementado:
- Se mantienen dos buffers separados: timeout y usados.
- Prioridad global: timeout antes que usados.
- Ambos buffers estan ordenados por `ready_at` con desempate por orden de insercion.
- Gap aleatorio: `RELEASE_GAP_RANGE_SECONDS = (1.0, 2.0)`.
- Cooldown usados: `USED_COLOR_COOLDOWN_RANGE_SECONDS = (8.0, 10.0)`.
- El total inicial de colores puede configurarse con `INITIAL_TOTAL_COLORS`, independiente de la concurrencia.
- Limite de concurrencia con reglas por vivos.

Evidencia:
- servidor/games/flare_curse/flare_curse_engine.py:54
- servidor/games/flare_curse/flare_curse_engine.py:55
- servidor/games/flare_curse/flare_curse_engine.py:62
- servidor/games/flare_curse/flare_curse_engine.py:500
- servidor/games/flare_curse/flare_curse_engine.py:718
- servidor/games/flare_curse/flare_curse_engine.py:723

## 2.6 Musica/intensidad

Spec:
- Score periodico con 3 factores (colores en mano, destellos recientes, maldiciones recientes).
- Umbral para cambiar calm/intense.

Implementado:
- Evaluacion periodica y score con pesos configurados en constantes de engine.
- Cambio de modo por hysteresis high/low.
- Emision de evento `MusicModeChanged`.
- Al finalizar la partida, el engine fuerza modo `intense` para la pantalla final.
- En host, los loops calm/intense se cargan en Web Audio API y arrancan sobre el mismo reloj de audio para maxima sincronizacion.
- El cambio entre modos usa crossfade suave por `GainNode` (`linearRampToValueAtTime`) sin silencios intencionales.

Evidencia:
- servidor/games/flare_curse/flare_curse_engine.py:673
- servidor/games/flare_curse/flare_curse_engine.py:632
- servidor/static/js/flare_curse/flare_curse_host.js:77
- servidor/static/js/flare_curse/flare_curse_host.js:156
- servidor/static/js/flare_curse/flare_curse_host.js:214
- servidor/static/js/flare_curse/flare_curse_host.js:235
- servidor/static/js/flare_curse/flare_curse_host.js:236

## 2.7 Socket protocol

Spec:
- Acciones cliente: `GetJugadores`, `PedirDestello`, `LanzarDestello`, `LanzarDestelloFantasma`, `Maldecir`.
- Eventos server: disponibilidad de destellos, timeout, flashes, maldiciones, fin.

Implementado:
- Consumer dedicado `FlareCurseRoom` con esas acciones y resultados.
- Snapshot inicial para jugador con nombre.
- Guardas de error: excepciones del engine se convierten en error controlado.
- Logging de connect/disconnect y fallos en acciones.

Evidencia:
- servidor/consumers.py:171
- servidor/consumers.py:242
- servidor/consumers.py:338

## 2.8 Frontend jugador/host

Spec:
- Jugador: boton de color, timer, tabla, maldecir, transicion a fantasma.
- Host: pantalla sin controles de juego.

Implementado:
- Player HTML+JS con panel vivo/fantasma, timer de mano/cooldown, tabla click para maldecir.
- Host HTML+JS escucha estado/eventos y vuelve al selector al final.
- Host muestra resumen final con tabla de maldiciones y leaderboard de fantasmas.
- En historial final se resaltan rebotes y aciertos con clases visuales diferenciadas.
- Cada cliente randomiza localmente el orden de jugadores al recibir snapshot inicial, de forma que cada jugador puede ver un orden distinto.
- En rol fantasma se oculta el panel de jugadores, quedando solo interfaz de fantasma (boton, cooldown y puntos).
- La lista de jugadores se renderiza como tarjetas cuadradas; al revelarse un equipo, el nombre se enmarca con forma visual: circulo, cuadrado o cuadrado ondulado para fantasma inicial.
- Timers visuales del cliente se derivan de `snapshot.timings` (hold/cooldown), sin hardcodear duraciones fijas.
- Integrado a rutas y websocket dedicados.

Evidencia:
- servidor/games/flare_curse/flare_curse_engine.py:181
- servidor/static/js/flare_curse/flare_curse_player.js:185
- servidor/static/js/flare_curse/flare_curse_player.js:315
- servidor/static/js/flare_curse/flare_curse_player.js:346
- servidor/static/js/flare_curse/flare_curse_player.js:512
- servidor/static/js/flare_curse/flare_curse_player.js:415
- servidor/static/js/flare_curse/flare_curse_player.js:428
- servidor/static/js/flare_curse/flare_curse_player.js:445
- servidor/static/js/flare_curse/flare_curse_host.js:315
- servidor/static/js/flare_curse/flare_curse_host.js:340
- servidor/static/js/flare_curse/flare_curse_host.js:342
- servidor/templates/flare_curse/flare_curse_player.html:38
- servidor/templates/flare_curse/flare_curse_player.html:107
- servidor/templates/flare_curse/flare_curse_player.html:158
- servidor/templates/flare_curse/flare_curse_host.html:101
- servidor/templates/flare_curse/flare_curse_host.html:105
- servidor/templates/flare_curse/flare_curse_host.html:120

## 2.9 Audio de voz (host)

Spec objetivo (iteraciones posteriores):
- Anunciar eventos clave con frases compuestas por contexto + equipo + jugador.

Implementado:
- Soporte de rutas de voz en host via `data-fc-voice-base`.
- Cola de reproduccion de clips para evitar solapes.
- Composicion de anuncio en `NuevoJugadorMaldito` y `FinJuego`.
- Estructura de assets documentada en README de audio.

Evidencia:
- servidor/templates/flare_curse/flare_curse_host.html:16
- servidor/static/js/flare_curse/flare_curse_host.js:417
- servidor/static/js/flare_curse/flare_curse_host.js:428
- servidor/static/js/flare_curse/flare_curse_host.js:450
- servidor/static/sounds/flare_curse/README_AUDIO.md:1

## 3. Cambios respecto a la spec original (y/o decisiones posteriores)

## 3.1 Cola FIFO -> lista ordenada por tiempo de liberacion

Cambio:
- En lugar de cola simple, timeout/usados estan ordenados por `ready_at` con desempate por orden de insercion.

Motivo:
- Evita bloquear un color listo por otro insertado antes pero no listo.

Evidencia:
- servidor/games/flare_curse/flare_curse_engine.py:742

## 3.2 Destello ofrecido sin timeout

Cambio:
- El color ofrecido no caduca por tiempo; se mantiene hasta que alguien lo reclama.

Motivo:
- Ajuste pedido en iteraciones posteriores.

Evidencia:
- servidor/games/flare_curse/flare_curse_engine.py:500
- servidor/games/flare_curse/test_flare_curse_engine.py:303

## 3.3 Configuracion centralizada solo en engine

Cambio:
- Se retiro la configuracion duplicada en `settings.py`.
- Los parametros viven solo como constantes del engine.

Motivo:
- Evitar doble fuente de verdad.

Evidencia:
- servidor/games/flare_curse/flare_curse_engine.py:50

## 3.4 Sin integracion economia/premios

Cambio:
- Se mantiene el juego aislado de sistema de monedas/premios.

Evidencia:
- servidor/games/flare_curse/flare_curse_engine.py:43

## 3.5 Contencion de fantasma "llegada tarde"

Cambio:
- Se agrego una ventana configurable post-apagado (`GHOST_POST_FACE_GRACE_SECONDS`) para no reiluminar al que acaba de apagarse.
- Si no hay objetivo alternativo fuera del conjunto activador, el destello fantasma no afecta a nadie.

Motivo:
- Reducir sensacion de injusticia por latencia o timing al borde del apagado.

Evidencia:
- servidor/games/flare_curse/flare_curse_engine.py:57
- servidor/games/flare_curse/flare_curse_engine.py:284
- servidor/games/flare_curse/flare_curse_engine.py:591
- servidor/games/flare_curse/test_flare_curse_engine.py:320
- servidor/games/flare_curse/test_flare_curse_engine.py:353

## 3.6 Resumen final host con resaltado de rebotes

Cambio:
- Se agregaron tablas finales de `curse_history` y `ghost_leaderboard`.
- Rebotes y aciertos se muestran con estilo visual distinto.

Evidencia:
- servidor/games/flare_curse/flare_curse_engine.py:667
- servidor/games/flare_curse/flare_curse_engine.py:668
- servidor/static/js/flare_curse/flare_curse_host.js:340
- servidor/templates/flare_curse/flare_curse_host.html:101

## 3.7 Musica host migrada a Web Audio sincronizado

Cambio:
- Reemplazo de mezcla basada en dos `HTMLAudio` por graph de Web Audio API con fuentes sincronizadas y crossfade por ganancia.

Motivo:
- Mejor sincronizacion cuando ambas pistas son variaciones de la misma cancion.

Evidencia:
- servidor/static/js/flare_curse/flare_curse_host.js:77
- servidor/static/js/flare_curse/flare_curse_host.js:156
- servidor/static/js/flare_curse/flare_curse_host.js:214

## 3.8 Total de colores inicial desacoplado de concurrencia

Cambio:
- Se agrego `INITIAL_TOTAL_COLORS` para elegir explicitamente cuantos colores totales entran en la partida.
- Si no se define (`None`), se conserva el comportamiento previo basado en reglas de concurrencia.
- El valor se acota a `[0, len(COLORS)]`.

Motivo:
- Permitir mas variedad total de colores en partida sin aumentar necesariamente colores concurrentes en mano.

Evidencia:
- servidor/games/flare_curse/flare_curse_engine.py:62
- servidor/games/flare_curse/flare_curse_engine.py:723
- servidor/games/flare_curse/flare_curse_engine.py:731
- servidor/games/flare_curse/test_flare_curse_engine.py:813
- servidor/games/flare_curse/test_flare_curse_engine.py:820

## 4. Diferencias funcionales pendientes vs spec

## 4.1 Audio centralizado en host (no en servidor)

Estado:
- La musica y voz se reproducen en cliente host.
- El servidor solo emite eventos y estado.

Impacto:
- Alineado con arquitectura web actual, pero distinto a una hipotetica mezcla/render de audio en backend.

## 4.2 Dependencia de assets de voz reales

Estado:
- La composicion y cola de voz estan implementadas.
- Si faltan clips concretos, se omiten y la cola continua.

Evidencia:
- servidor/static/sounds/flare_curse/README_AUDIO.md:75

## 4.3 UI de jugador: pequenas desviaciones

Pendiente o distinto:
- No hay confirmacion previa al click de maldicion (queda en backlog de UX).

Evidencia:
- servidor/static/js/flare_curse/flare_curse_player.js:354

## 4.4 Campo `at_seconds` en payload de historial

Estado:
- El engine sigue emitiendo `at_seconds` por registro.
- La UI host no lo muestra en tablas finales.

Evidencia:
- servidor/games/flare_curse/flare_curse_engine.py:354
- servidor/static/js/flare_curse/flare_curse_host.js:336

## 5. Cobertura de testing actual

Implementado:
- Tests de engine: reglas de juego, tiempos, colas, fin de partida, musica, no economia, historial y leaderboard.
- Tests de engine para contencion fantasma: competencia entre fantasmas del mismo color, exclusion de recien apagados y caso sin objetivo alternativo.
- Tests de consumer: contrato de mensajes, errores controlados, guardas de excepcion.
- Smoke multicliente: broadcast global, evento privado y aislamiento de respuesta por emisor.

Evidencia:
- servidor/games/flare_curse/test_flare_curse_engine.py:132
- servidor/games/flare_curse/test_flare_curse_engine.py:286
- servidor/games/flare_curse/test_flare_curse_engine.py:320
- servidor/games/flare_curse/test_flare_curse_engine.py:353
- servidor/games/flare_curse/test_flare_curse_engine.py:646
- servidor/games/flare_curse/test_flare_curse_consumer.py:190
- servidor/games/flare_curse/test_flare_curse_consumer.py:294

Resultado observado en esta rama:
- Suite Flare Curse completa en verde: 66 tests pasando.

## 6. Conclusiones

- El nucleo de gameplay y deduccion social esta implementado y testeado.
- El juego funciona como modo standalone en el flujo general de la plataforma.
- Las iteraciones recientes cerraron tres brechas importantes: contencion de timing para fantasmas, resumen final host legible, y audio host sincronizado con crossfade suave.
- Los pendientes principales quedan acotados a refinamientos de UX de jugador y limpieza opcional de payloads.
