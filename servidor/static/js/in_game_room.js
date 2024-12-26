// Join the in game room and return the socket
async function join_in_game_room()
{
    let in_game_room_url = `ws://${window.location.host}/ws/in_game_room/`;
    let in_game_room_socket = new WebSocket(in_game_room_url);
    await new Promise(resolve => in_game_room_socket.addEventListener("open", resolve));
    return in_game_room_socket;
}

// Player notifies the admin that he has interacted with the game
async function notify_player_has_interacted()
{
    in_game_room_socket = await join_in_game_room();
    in_game_room_socket.send(JSON.stringify({
        'player_has_interacted': true,
    }));
    console.log("Player has interacted")
    in_game_room_socket.close();
}

/* Admin listens in the in game room socket and when all players have interacted
he proceeds with calling the function passed as parameter
*/
async function listen_in_game_room()
{
    in_game_room_socket = await join_in_game_room();
    set_can_players_interact(true);
    console.log("Admin is listening in game room")
    return new Promise(function(resolve, reject) {
        in_game_room_socket.onmessage = function(e) {
            console.log("All players have interacted")
            in_game_room_socket.close();
            set_can_players_interact(false);
            resolve();
        };
    });
}

/*
Admin listens continuously in the in game room socket 
When a message is received:
- it checks if the message is an admin update needed, if so, it calls the function passed as parameter
- if not, the game has ended, if so, it resolves the promise and closes the socket
*/
async function listen_in_game_room_continuously(refresh_game_data_from_server) {
    in_game_room_socket = await join_in_game_room();
    set_can_players_interact(true);
    return new Promise(async (resolve, reject) => {
      console.log("Admin is continuously listening in game room");
  
      in_game_room_socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
  
        if (data.admin_update_needed === true) {
          console.log("Server told admin to refresh data!");
          refresh_game_data_from_server();
        }
        else {
          console.log("Game has ended");
          in_game_room_socket.close();
          set_can_players_interact(false);
          // Now we can resolve the promise
          resolve();
        }
      };
  
      in_game_room_socket.onerror = function(err) {
        reject(err);
      };
    });
  }