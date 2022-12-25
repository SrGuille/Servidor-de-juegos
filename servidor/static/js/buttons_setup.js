//Create a new button in the buttons row
function add_button(left, top, id, button_class) 
{
    buttons_row = document.getElementById("buttons_row");
    new_button = document.createElement("button");
    new_button.id = id;
    new_button.className = button_class;
    new_button.style = "top: " + top + "px; left: " + left + "px";
    new_button.onclick = function() {bet_unbet(this)};
    buttons_row.appendChild(new_button);
}

function load_regular_numbers_buttons()
{
    horizontal_step = 55;
    vertical_step = 73;

    initial_left = 121;
    initial_top = 54;

    //Create the buttons in numerical order to assign the correct id
    id = 1;
    for(i = 0; i < 12; i++)
    {
        for(j = 2; j >= 0; j--)
        {
            button_left = initial_left + i * horizontal_step;
            button_top = initial_top + j * vertical_step;
            button_id = id;
            add_button(button_left, button_top,  button_id, "button-number");
            id++;
        }
    }
}

function load_third_buttons()
{
    initial_left = 121;
    button_top = 275;
    horizontal_step = 220;

    ids_th = ["1T", "2T", "3T"]

    for(i = 0; i < 3; i++)
    {
        button_left = initial_left + i * horizontal_step;
        add_button(button_left, button_top,  ids_th[i], "button-third");
    }
}

function load_row_buttons()
{
    button_left = 781;
    initial_top = 54;
    vertical_step = 73;

    ids_row = ["1R", "2R", "3R"]

    for(j = 0; j < 3; j++)
    {
        button_top = initial_top + j * vertical_step;
        add_button(button_left, button_top,  ids_row[j], "button-row");
    }

}

function load_half_buttons()
{
    initial_left = 121;
    button_top = 335;
    horizontal_step = 110;

    ids_hf = ["1H", "E", "R", "B", "O", "2H"]

    for(i = 0; i < 6; i++)
    {
        button_left = initial_left + i * horizontal_step;
        add_button(button_left, button_top,  ids_hf[i], "button-half");
    }
}

function buttons_setup()
{
    load_regular_numbers_buttons();
    load_third_buttons();
    load_row_buttons();
    load_half_buttons();
    add_button(60, 127, 0, "button-number");
}