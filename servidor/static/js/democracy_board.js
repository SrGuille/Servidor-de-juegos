rows = 10;
cols = 10;
classes = ['blue-cell', 'orange-cell']
x = 0;
y = 0;
colors_per_second = Array();

horizontal_step = 100;
vertical_step = 100;
initial_left = 700;
initial_top = 10;

var logical_board = new Array(rows);

async function play_game()
{
    await load_board();
    await create_teams();
    ready_to_play_game()
    await new Promise(r => setTimeout(r, 10000)); //Wait 10 seconds
    await countdown();
    await start_game();
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
    assign_cells();
    show_board_cells();
    add_character(5,5); //Add the character in the middle of the board
    console.log(logical_board)
}

//Create a new button in the buttons row
function add_cell(left, top, color) 
{
    board = document.getElementById("board");
    console.log(board)
    new_cell = document.createElement("div");
    new_cell.className = color;
    new_cell.style = "top: " + top + "px; left: " + left + "px";
    board.appendChild(new_cell);
}

// Initialize the logical board with 0s
function init_logical_board()
{
    for(i = 0; i < rows; i++)
    {
        logical_board[i] = new Array(cols);
        
        for(j = 0; j < cols; j++)
        {
            logical_board[i][j] = 0;
        }
    }
}

// Assign the cells to the second team
function assign_cells()
{
    cells_team_2 = get_cells_for_team();
    console.log(cells_team_2)

    for(i = 0; i < cells_team_2.length; i++)
    {
        cell = cells_team_2[i];
        row = Math.floor(cell / cols);
        col = cell % cols;
        logical_board[row][col] = 1;
    }
}

// Randomly generate a set with half of the cells numbers
function get_cells_for_team()
{
    total_cells = rows * cols;
    cells_for_each_team = total_cells / 2;
    const cells = new Set();
    while(cells.size !== cells_for_each_team) 
    {
        cells.add(Math.floor(Math.random() * total_cells - 1) + 1);
    }
    return Array.from(cells);
}

// Show the cells in the board
function show_board_cells()
{
    // Create the all the divs
    for(i = 0; i < rows; i++)
    {
        for(j = 0; j < cols; j++)
        {
            cell_left = initial_left + i * horizontal_step;
            cell_top = initial_top + j * vertical_step;
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
    x = mod(x + x_moves, cols);
    y = mod(y + y_moves, rows);

    console.log(x,y)

    cell_left = initial_left + x * horizontal_step;
    cell_top = initial_top + y * vertical_step;

    character = document.getElementById("character");
    character.style = "top: " + cell_top + "px; left: " + cell_left + "px";
}

async function start_game()
{
    round = 0;
    max_rounds = 30;
    while(round < max_rounds)
    {
        await new Promise(r => setTimeout(r, 1000)); //Wait 1 seconds
        move_with_democracy();
        round += 1;
    }
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
            colors_per_second.push(logical_board[x][y]);
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
