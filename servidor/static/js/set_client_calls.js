function tell_server_to_stop_listening_calls()
{
    $.ajax({
        url: '../dont_listen_client_calls/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8'
    });
}


function tell_server_to_start_listening_calls()
{
    // Listen to client calls
    $.ajax({
        url: '../listen_client_calls/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8'
    });
}
