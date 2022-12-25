// Table rows for ranking
async function get_ranking()
{
    ranking_table = document.getElementById("ranking");

    $.ajax({
        url: '../get_ranking/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        success: function(ranking) 
        {
            console.log(ranking);
            for(i = 0; i < ranking.length; i++)
            {
                ranking_row = document.createElement("tr");
                
                player_name = document.createElement("td");
                player_name.innerHTML = ranking[i].player_name;
                ranking_row.appendChild(player_name);
                
                player_coins = document.createElement("td");
                player_coins.innerHTML = ranking[i].coins;
                ranking_row.appendChild(player_coins);

                ranking_table.appendChild(ranking_row);
            }
        }
    });

    create_prizes_roulette()

}

function create_prizes_roulette()
{
    prizes_roulette = document.getElementById("prizes_roulette");

    $.ajax({
        url: '../get_pie_chart/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        success: function(result) 
        { 
            pie_chart = document.createElement("img");
            pie_chart.src = "/static/img/pie_chart.png";
            prizes_roulette.appendChild(pie_chart);
        }
    });
}
