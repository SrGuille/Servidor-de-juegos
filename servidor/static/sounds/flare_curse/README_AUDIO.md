# Flare Curse audio layout

Put the real audio assets in this folder structure.

## Music loops

- `loop_calm.mp3`
- `loop_intense.mp3`

## Voice tracks

Folder: `voices/`

### Context clips (`voices/context/`)

- `del_equipo.mp3`
- `ha_sido_maldito.mp3`
- `el_juego_ha_terminado.mp3`
- `ha_ganado_el_equipo.mp3`
- `con_word.mp3`
- `fantasmas_ganadores.mp3`

### Team clips (`voices/teams/`)

- `circulo.mp3`
- `cuadrado.mp3`

### Player clips (`voices/players/`)

Use the same token format as the websocket player group sanitizer:
- lowercase
- remove diacritics
- keep `a-z`, `0-9`, `.` and `-`
- replace other characters with `-`
- trim to 60 chars

Examples:
- `Ana Foo@1` -> `ana-foo-1.mp3`
- `Andres` -> `andres.mp3`
- `Toña` -> `tona.mp3`

## Current player filenames (from DB)

### All players

- `ainara.mp3`
- `ale.mp3`
- `ana.mp3`
- `andres.mp3`
- `cris.mp3`
- `diego.mp3`
- `fano.mp3`
- `guille.mp3`
- `isa.mp3`
- `juanda.mp3`
- `marcosa.mp3`
- `marcost.mp3`
- `nayla.mp3`
- `rafa.mp3`
- `stef.mp3`
- `tona.mp3`

### Currently logged players

- `ainara.mp3`
- `ale.mp3`
- `ana.mp3`
- `andres.mp3`
- `cris.mp3`
- `diego.mp3`
- `fano.mp3`
- `guille.mp3`
- `juanda.mp3`
- `marcosa.mp3`
- `marcost.mp3`
- `nayla.mp3`
- `rafa.mp3`
- `stef.mp3`
- `tona.mp3`

Note:
- Missing clips are skipped gracefully at runtime. The queue continues with the next clip.
- On Windows, avoid reserved device names such as `con`, `nul`, `prn`, `aux`, `com1`, etc. as bare filenames.
