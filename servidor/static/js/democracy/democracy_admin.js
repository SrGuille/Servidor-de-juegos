// Always odd numbers to have a central neutral cell
ROWS = 19;
COLS = 19;
CENTRAL_CELL_X = Math.floor((ROWS) / 2);
CENTRAL_CELL_Y = Math.floor((COLS) / 2);

classes = ['neutral-cell', 'green-cell', 'red-cell']

MAX_ROUNDS = 32;

// Character position
x = 0;
y = 0;

colors_per_second = Array();

// Proporciones base (ratio ancho:alto = 2:1)
cell_aspect_ratio = 2; // ancho es 2x el alto
character_scale = 1.4; // escala del personaje respecto a la celda

// Dimensiones calculadas dinámicamente
var cell_width = 0;
var cell_height = 0;
var character_width = 0;
var character_height = 0;
var character_margin_x = 0;
var character_margin_y = 0;

// Calcula las dimensiones de las celdas para que quepan en la pantalla
function calculate_cell_dimensions()
{
    // Margen para el contenedor y espacio para el contador superior
    var margin = 40;
    var top_space = 120; // Espacio para el contador (margin-top del board + altura del contador)
    var available_width = window.innerWidth - margin;
    var available_height = window.innerHeight - margin - top_space;
    
    // Calcular tamaño máximo que cabe
    var max_cell_width = available_width / COLS;
    var max_cell_height = available_height / ROWS;
    
    // Ajustar según la proporción (ancho = alto * ratio)
    // Si el ancho limita:
    var cell_width_from_width = max_cell_width;
    var cell_height_from_width = cell_width_from_width / cell_aspect_ratio;
    
    // Si el alto limita:
    var cell_height_from_height = max_cell_height;
    var cell_width_from_height = cell_height_from_height * cell_aspect_ratio;
    
    // Elegir el que quepa
    if (cell_width_from_width <= max_cell_width && cell_height_from_width <= max_cell_height) {
        cell_width = cell_width_from_width;
        cell_height = cell_height_from_width;
    } else {
        cell_width = cell_width_from_height;
        cell_height = cell_height_from_height;
    }
    
    // Calcular dimensiones del personaje
    character_width = cell_width * character_scale;
    character_height = cell_height * character_scale;
    character_margin_x = (cell_width - character_width) / 2;
    character_margin_y = (cell_height - character_height) / 2;
}

// Variables para posición del board (se calculan dinámicamente)
var board_offset_left = 0;
var board_offset_top = 0;

// Dirección del personaje: true = derecha, false = izquierda
var character_facing_right = true;

var logical_board = new Array(ROWS);

async function play_democracy()
{
    // Mostrar texto inicial
    document.getElementById("rounds_left").innerHTML = "Cargando...";
    
    await load_board();
    console.log("Board loaded")
    await create_teams();
    console.log("Teams created")
    await new Promise(r => setTimeout(r, 10000)); //Wait 10 seconds
    await countdown();
    await set_can_players_interact(true); // Players can move
    await main_loop(); 
    await set_can_players_join(false);
    await set_can_players_interact(false); // Players can't move
    await new Promise(r => setTimeout(r, 5000)); //Wait 5 seconds
    console.log(colors_per_second)
    await send_colors_per_second();
    await new Promise(r => setTimeout(r, 3000)); //Wait 3 seconds
    window.location.href = "../ranking_and_prizes/";
    
}

async function countdown()
{
    document.getElementById("enable_sounds").click(); // Trick browser to enable sounds
    arcade_jump_audio.volume = 0.7;
    arcade_jump_audio.play();
    var rounds_left = document.getElementById("rounds_left");
    for(i = 3; i > 0; i--)
    {
        rounds_left.innerHTML = i;
        arcade_jump_audio.play();
        await new Promise(r => setTimeout(r, 1000)); //Wait 1 seconds
        arcade_jump_audio.pause();
    }
    rounds_left.innerHTML = "¡GO!";
    await new Promise(r => setTimeout(r, 500));
}

async function load_board()
{   
    calculate_cell_dimensions(); // Calcular dimensiones responsive
    init_logical_board();
    assign_cells();
    show_board_cells();
    add_character(CENTRAL_CELL_X, CENTRAL_CELL_Y); // Start in the central cell
    console.log(logical_board)
}

//Create a new cell in the board grid
function add_cell(color) 
{
    board = document.getElementById("board");
    new_cell = document.createElement("div");
    new_cell.className = color;
    board.appendChild(new_cell);
}

// Initialize the logical board with 1s (team 1) and a 0 in the central cell (neutral)
function init_logical_board()
{
    for(i = 0; i < ROWS; i++)
    {
        logical_board[i] = new Array(COLS);
        
        for(j = 0; j < COLS; j++)
        {
            logical_board[i][j] = 1;
        }
    }

    // Set the central cell to 0 (neutral)
    logical_board[Math.floor(ROWS / 2)][Math.floor(COLS / 2)] = 0;
}

// Assign half of the cells to the second team with 2s
function assign_cells()
{
    cells_team_2 = get_cells_for_team();

    for(i = 0; i < cells_team_2.length; i++)
    {
        cell = cells_team_2[i];
        row = Math.floor(cell / COLS);
        col = cell % COLS;
        console.log(row,col)
        logical_board[row][col] = 2;
    }
    
}

// Randomly generate a set with half of the cells numbers
function get_cells_for_team()
{
    total_cells = ROWS * COLS;
    cells_for_each_team = Math.floor(total_cells / 2);

    // Include the central cell to later remove it
    central_cell = Math.floor(total_cells / 2);
    const cells = new Set();
    cells.add(central_cell);

    while(cells.size !== cells_for_each_team + 1) // +1 because of the central cell
    {
        // Generate a random number between 1 and total_cells
        random_cell = Math.floor(Math.random() * total_cells - 1) + 1;
        cells.add(random_cell); // If it is already in the set it is ignored
    }
    cells.delete(central_cell); 
    return Array.from(cells);
}

// Show the cells in the board
function show_board_cells()
{
    board = document.getElementById("board");
    // Set CSS Grid columns based on COLS and cell dimensions
    board.style.gridTemplateColumns = "repeat(" + COLS + ", " + cell_width + "px)";
    board.style.gridTemplateRows = "repeat(" + ROWS + ", " + cell_height + "px)";
    
    // Create the all the divs (row-major order for CSS Grid)
    for(j = 0; j < ROWS; j++)
    {
        for(i = 0; i < COLS; i++)
        {
            add_cell(classes[logical_board[i][j]]);
        }
    }
}

function add_character(initial_x,initial_y)
{
    board = document.getElementById("board");
    
    // Eliminar personaje existente si hay uno
    var existing_character = document.getElementById("character");
    if(existing_character) {
        existing_character.remove();
    }
    
    character = document.createElement("img");
    character.id = "character";
    character.className = "character";
    character.src = "/static/img/democracia/hat_sprite.svg";
    board.appendChild(character);
    
    // Calcular offset del board para posicionar el personaje
    update_board_offset();
    move_character(initial_x, initial_y)
}

// Actualiza las coordenadas del board para el personaje
function update_board_offset()
{
    board = document.getElementById("board");
    rect = board.getBoundingClientRect();
    board_offset_left = rect.left + window.scrollX;
    board_offset_top = rect.top + window.scrollY;
}

// Modulo function that works with negative numbers
function mod(n, m) 
{
    return ((n % m) + m) % m;
}

function move_character(x_moves, y_moves)
{
    old_x = x;
    x = mod(x + x_moves, COLS);
    y = mod(y + y_moves, ROWS);

    console.log("x_moves:", x_moves, "y_moves:", y_moves);

    // Actualizar dirección solo si hay movimiento horizontal real
    if(x_moves > 0) {
        character_facing_right = true;
        console.log("FLIP: mirando a la DERECHA (x_moves > 0)");
    } else if(x_moves < 0) {
        character_facing_right = false;
        console.log("FLIP: mirando a la IZQUIERDA (x_moves < 0)");
    } else {
        console.log("Sin flip horizontal, x_moves =", x_moves, ", facing_right =", character_facing_right);
    }

    console.log("Posición:", x, y, "facing_right:", character_facing_right);

    // Posición relativa dentro del board
    cell_left = x * cell_width + character_margin_x;
    cell_top = y * cell_height + character_margin_y;

    // Rotación 90 grados a la derecha, o -90 si mira a la izquierda
    var transform = "rotate(90deg)";
    if(!character_facing_right) {
        transform = "rotate(-90deg)";
        console.log("Aplicando rotate(-90deg) para izquierda");
    }
    console.log("Transform aplicado:", transform);

    character = document.getElementById("character");
    character.style = "top: " + cell_top + "px; left: " + cell_left 
        + "px; width: " + character_width + "px; height: " + character_height + "px; transform: " + transform + ";";
}

// Initialize the clock
async function init_clock()
{
    await $.ajax({
        url: "../init_clock",
        type: "GET",
        success: function(response) {
            console.log("Clock initialized");
        }
    });
}

async function main_loop()
{
    corriendo_en_la_noche.volume = 0.2;
    corriendo_en_la_noche.play();
    round = 0;
    rounds_left = document.getElementById("rounds_left");
    
    init_clock(); // Initialize the clock
    while(round < MAX_ROUNDS)
    {
        rounds_left.innerHTML = "Fin en " + (MAX_ROUNDS - round).toString();
        await new Promise(r => setTimeout(r, 1000)); //Wait 1 second
        arcade_jump_audio.play();
        move_with_democracy();
        round += 1;
    }
    rounds_left.innerHTML = "Fin!";
    await new Promise(r => setTimeout(r, 2000)); //Wait 2 seconds
}

async function create_teams()
{
    await $.ajax({
        url: "../create_teams_democracy",
        type: "GET",
        success: function(response) {
            console.log(response.teams);
        }
    });
}

// Get democratic move, move the character and log the color
async function move_with_democracy()
{
    await $.ajax({
        url: "../get_democratic_move",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        success: function(response) 
        {
            horizontal_force = response.horizontal_force;
            vertical_force = response.vertical_force;
            move_character(horizontal_force, vertical_force);
            if(logical_board[x][y] != 0) // If it is not neutral
            {
                colors_per_second.push(logical_board[x][y]);
            }
            console.log(x,y)
        }
    });
}

// Send the colors per second to the server
async function send_colors_per_second()
{
    response = await $.ajax({
        url: "../send_colors_per_second",
        type: "GET",
        data: {'colors_per_second': JSON.stringify(colors_per_second)},
        contentType: 'application/json;charset=UTF-8'
    });

    winner_msj = response.winner_msj;
    showVictoryModal(winner_msj);
}

// Show the victory modal with the result message
function showVictoryModal(message) {
    const modalOverlay = document.getElementById("victory-modal-overlay");
    const modalContent = document.getElementById("victory-modal-content");
    modalContent.innerHTML = message;
    modalOverlay.classList.add("show");
}
