import random

oraciones_str = [
    """Las mascotas ladraban sin cesar, el vecino se quejó con sus dueños.
    Amalia es una buena amiga, pero Clara no lo ve.
    La joven lloró toda la noche, pero su amiga logró consolarla.
    La madre cuenta un cuento y la niña junta sus juguetes.
    Ana prepara la comida y Pedro se ocupa de la mesa.
    Andrea comió mucho y debió tomar un té digestivo.
    Cada mañana Teresa y Antonio desayunaban juntos, pero el silencio se hizo presente de a poco.
    Los niños no quieren quedarse en casa, aunque el día esté lluvioso.
    Los perros robaron la comida y luego huyeron.
    Mi madre viajó a Buzios, mientras que mi padre se fue a Canadá.
    La niña sintió mucho miedo; su hermano mayor se rio de ella.
    Al cerrar las persianas, el viento comenzó a soplar con más fuerza y escuchamos un ruido muy fuerte.
    Constanza se enamoró de Juan; él solo piensa en Sofía.
    El pasajero perdió el bus y la empresa no se hace cargo.
    El diario publicó una nota que el editor había prohibido.
    La comida estaba demasiado salada, los invitados casi no comieron.
    El dinero estaba en la caja de seguridad y el sospechoso lo sabía.
    Ella se quedó dormida, él la miró con amor.
    Cometió un error y su amigo no quiere perdonarla.
    La muchacha pintó un cuadro hermoso y se siente orgullosa.
    Isabel llamó a su hermano para su cumpleaños y él se puso contento.
    El hombre se despertó muy resfriado y el médico le indicó reposo.
    La montaña era difícil de escalar, pero el alpinista no tenía miedo.
    La música que compuso era para una joven, pero ella no la escuchó jamás.
    La noche estaba estrellada y los amantes se besaron.
    Alejandro quería hablar con Matilde, pero no la encontró.
    La película terminó y el público se quedó en silencio.
    La tarde estaba hermosa, por eso salí a caminar por el parque.
    Las hormigas atacaron el árbol y María se entristeció.
    Las niñas actuaron muy bien, pero se cortó la luz a último momento.
    El cielo quedó despejado y pronto se asomó el sol.
    Las ventanas estaban abiertas y entraron muchas libélulas a la casa.
    Las zapatillas están de liquidación, por eso Juan se compró dos pares.
    Lucas partió en el primer tren, pero igualmente llegó tarde.
    Las personas no entienden la importancia del cuidado del agua y el planeta no puede seguir esperando.
    Marcelo compró una casa grande, sus hijas estaban muy contentas.
    La artista canta muy bien, aunque muchos la critiquen.
    Mientras los niños pasean enojados por el parque, los padres caminan felices.
    Tengo que avisarte que ese negocio no es una buena idea.
    El perro ladra y los gatos se esconden.
    Queremos saber más sobre cómo llegaste a salvo a la civilización.
    Estoy cantando la canción que me enseñaste.
    El viaje comenzó sin inconvenientes; nadie imaginó lo que ocurriría después.
    Sabes que te quiero.
    El niño quiere que le compren dulces y se pone caprichoso.
    Finalmente, llegamos al lugar donde viví cuando mis padres aún no habían comprado su casa actual.
    Todos fuimos a comer al lugar que nos recomendaste.
    La canción era muy dulce y la mujer se emocionó.
    La casa está limpia y las cortinas brillan.
    Llegó el gran día: hoy se recibe mi hijo."""
]

oraciones = [oracion.split() for oracion in oraciones_str]

def get_random_sentence():
    oracion = random.choice(oraciones)
    oraciones.remove(oracion)
    return oracion