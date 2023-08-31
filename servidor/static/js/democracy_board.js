// Always odd numbers to have a central neutral cell
ROWS = 15;
COLS = 15;
classes = ['neutral-cell', 'blue-cell', 'orange-cell']
x = 0;
y = 0;
colors_per_second = Array();

cell_size = 50; // 50x50 px
cell_padding = cell_size / 2; // 25px
initial_left = 750;
initial_top = 150;
character_size = 30; // 30x30 px
character_margin = (cell_size - character_size) / 2; // 10px

var logical_board = new Array(ROWS);

async function play_democracy()
{
    await load_board();
    console.log("Board loaded")
    await create_teams();
    console.log("Teams created")
    ready_to_play_game()
    await new Promise(r => setTimeout(r, 10000)); //Wait 10 seconds
    await countdown();
    await main_loop(); 
    await new Promise(r => setTimeout(r, 5000)); //Wait 5 seconds
    console.log(colors_per_second)
    send_colors_per_second();
    await new Promise(r => setTimeout(r, 10000)); //Wait 5 seconds
    window.location.href = "../ranking/";
    
}

async function countdown()
{
    for(i = 3; i > 0; i--)
    {
        document.getElementById("countdown").innerHTML = i;
        await new Promise(r => setTimeout(r, 1000)); //Wait 1 seconds
    }
    document.getElementById("countdown").innerHTML = "";
}

async function load_board()
{
    init_logical_board();
    console.log("Logical board initialized")
    assign_cells();
    console.log("Cells assigned")
    show_board_cells();
    console.log("Board cells shown")
    add_character(7,7);
    console.log("Character added")
    console.log(logical_board)
}

//Create a new button in the buttons row
function add_cell(left, top, color) 
{
    board = document.getElementById("board");
    console.log(board)
    new_cell = document.createElement("div");
    new_cell.className = color;
    new_cell.style = "top: " + top + "px; left: " + left + "px" + "; padding: " + cell_padding + "px;";
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
    // Create the all the divs
    for(i = 0; i < ROWS; i++)
    {
        for(j = 0; j < COLS; j++)
        {
            cell_left = initial_left + i * cell_size;
            cell_top = initial_top + j * cell_size;
            add_cell(cell_left, cell_top, classes[logical_board[i][j]]);
        }
    }
}

function add_character(initial_x,initial_y)
{
    board = document.getElementById("board");
    character = document.createElement("div");
    character.id = "character";
    character.className = "character";
    board.appendChild(character);
    move_character(initial_x, initial_y)
}

// Modulo function that works with negative numbers
function mod(n, m) 
{
    return ((n % m) + m) % m;
}

function move_character(x_moves, y_moves)
{
    x = mod(x + x_moves, COLS);
    y = mod(y + y_moves, ROWS);

    console.log(x,y)

    cell_left = initial_left + x * cell_size;
    cell_top = initial_top + y * cell_size;

    character = document.getElementById("character");
    character.style = "top: " + cell_top + "px; left: " + cell_left 
        + "px; margin: " + character_margin + "px; width: " 
        + character_size + "px; height: " + character_size + "px;";
}

async function main_loop()
{
    round = 0;
    max_rounds = 30;
    rounds_left = document.getElementById("rounds_left");
    while(round < max_rounds)
    {
        rounds_left.innerHTML = "Fin en " + (max_rounds - round).toString();
        await new Promise(r => setTimeout(r, 1000)); //Wait 1 seconds
        move_with_democracy();
        round += 1;
    }
    rounds_left.innerHTML = "Fin!";
    await new Promise(r => setTimeout(r, 2000)); //Wait 1 seconds
    not_ready_to_play_game()
}

async function create_teams()
{
    await $.ajax({
        url: "../create_teams",
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

    document.getElementById("result_democracy").innerHTML = response.winner_msj;
}
