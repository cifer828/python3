
var btn_at = []; // next button to be painted for each column
var grid_len = 6;
var grid = []; // 2d grid, 1 for blue player, -1 for red player
var firstPlayer = "blue player";
var secondPlayer = "red player";


// add buttons, fill the grid entries with default 0
function create_grid(len){
    var table = $("table").get(0);
    for (var i = 0; i < len; i++){
        var line = [];
        var row = table.insertRow(i); // add a row
        for(var j = 0; j < len; j++) {
            line.push(0);
            var cell = row.insertCell(j);
            var btn = document.createElement("button");
            $(btn).click({param1: i, param2: j}, oneMove);
            cell.appendChild(btn); // add cell in row
        }
        grid.push(line);
        btn_at.push(len - 1);
    }

}
var first = true;

// player wins if he has four connected chips in a row
function win(row){
    var conn = 0;
    for (var i = 1; i < grid_len; i++){
        if (grid[row][i] * grid[row][i - 1] === 1) {
            if (++conn >= 3)
                break;
        }
        else
            conn = 0;
    }
    if (conn >= 3){
        $('h2').hide();
        $('h3').hide();
        if (first) {
            $("h1").text(firstPlayer + " has won! Refresh your browser to play again!").css("color", "blue");
        }
        else
            $("h1").text(secondPlayer + " has won! Refresh your browser to play again!").css("color", "red");
    }
    return conn >= 3;
}

function oneMove(event){
    // method 1:
    // var col = $(this).index();
    // method 2:
    var col = event.data.param2;
    if (btn_at[col] < 0) return;
    // console.log(row + " " + col);
    var color_btn = $("table tr").eq(btn_at[col]).find("td").eq(col).find("button");

    if (first) {
        grid[btn_at[col]][col] = 1;
        color_btn.css("background-color", "blue");
        $("h3").text(secondPlayer + ": it is your turn, please pick a column to drop your red chip.");
    }
    else {
        grid[ btn_at[col]][col] = -1;
        color_btn.css("background-color", "red");
        $("h3").text(firstPlayer + ": it is your turn, please pick a column to drop your blue chip.");
    }
    if (win(btn_at[col]))
        disableBtn();

    btn_at[col]--; // move up next colored button
    first = !first; // change player
}

function newGame(){
    firstPlayer = prompt("Player One: Enter Your Name , you will be Blue");
    secondPlayer = prompt("Player Two: Enter Your Name, you will be Red");
    create_grid(grid_len);
    $("h3").text(firstPlayer + ": it is your turn, please pick a column to drop your blue chip.");
}

// freeze the button

function disableBtn(){
    var buttons = $("button");
    for (var i = 0; i < buttons.length; i++){
        buttons.eq(i).off("click", oneMove);
    }
}

newGame(grid_len);