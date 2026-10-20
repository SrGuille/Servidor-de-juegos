let num_socks = 8;
let rounds = 5;

brillos = "/static/img/calcetines/brillos.svg";
peste = "/static/img/calcetines/peste.svg";

async function initialize_admin_socks() {
    // Inicializa los calcetines y oculta los que sobren
    await $.ajax({
        url: '../initialize_socks',
        type: 'GET',
        success: function(response) {
            console.log("Initialize socks response:", response);
            num_socks = response.num_socks || 8;
            for (let i = 0; i < 8; i++) {
                const sockItem = document.getElementById('sock-item-' + i);
                if (sockItem) {
                    if (i < num_socks) {
                        sockItem.style.display = '';
                    } else {
                        sockItem.style.display = 'none';
                    }
                }
            }
        }
    });
}

async function show_socks_data(socks_data_msjs) {
    for (let i = 0; i < num_socks; i++) {
        let infoDiv = document.getElementById('sock-info-' + i);
        if (infoDiv) infoDiv.innerHTML = socks_data_msjs[i] || '';
    }
}


function addSockBadge(sockIdx, imgSrc, altText) {
    let sockSquare = document.getElementById('sock-' + sockIdx);
    if (sockSquare) {
        // Elimina badge anterior si existe
        let badge = sockSquare.querySelector('.sock-badge');
        if (badge) badge.remove();
        // Crea y añade la imagen
        let img = document.createElement('img');
        img.src = imgSrc;
        img.alt = altText;
        img.className = 'sock-badge';
        img.style.position = 'absolute';
        img.style.top = '0px';
        img.style.left = '50%';
        img.style.transform = 'translateX(-50%)';
        img.style.width = '200px';
        img.style.height = 'auto';
        img.style.pointerEvents = 'none';
        sockSquare.style.position = 'relative';
        sockSquare.appendChild(img);
    }
}

async function show_average_performance() {
    await $.ajax({
        url: '../get_socks_average_performance',
        type: 'GET',
        success: function(response) {
            console.log("Average performance response:", response);
            let perf = response.socks_average_performance;
            // Mostrar el número de cada sock en el cuadro de texto
            for (let i = 0; i < num_socks; i++) {
                let infoDiv = document.getElementById('sock-info-' + i);
                if (infoDiv) infoDiv.innerHTML = 'Premios promedio: x' + perf[i];
            }
            // Buscar los dos mejores y dos peores
            let arr = perf.map((val, idx) => ({idx, val}));
            arr.sort((a, b) => b.val - a.val);
            let best = arr.slice(0, 2);
            let worst = arr.slice(-2);
            best.forEach(b => addSockBadge(b.idx, brillos, 'Mejor calcetín'));
            worst.forEach(w => addSockBadge(w.idx, peste, 'Peor calcetín'));
            console.log('Mejores:', best);
            console.log('Peores:', worst);
        }
    });
}

async function socks_admin_game() {
    await initialize_admin_socks();
    for (let round = 0; round < rounds; round++) {
        // Notificar a los clientes que la ronda está lista
        await notify_clients_game_ready(5);
        // Esperar a que todos estén listos
        await listen_in_game_room();
        // Ejecutar la ronda y mostrar los datos
        await new Promise(r => setTimeout(r, 2000)); // Esperar 2 segundos antes de ejecutar la ronda
        await $.ajax({
            url: '../run_socks_round',
            type: 'GET',
            success: function(response) {
                console.log("Run round response:", response);
                let socks_data_msjs = response.socks_data_msjs;
                show_socks_data(socks_data_msjs);
            }
        });
    }
    await new Promise(r => setTimeout(r, 5000)); // Esperar 5 segundos antes de finalizar el juego
    // Al final, mostrar el rendimiento medio
    await show_average_performance();
    await new Promise(r => setTimeout(r, 10000)); // Esperar 10 segundos antes de finalizar el juego
    window.location.href = "../ranking_and_prizes/";
}

document.addEventListener('DOMContentLoaded', function() {
    socks_admin_game();
});
