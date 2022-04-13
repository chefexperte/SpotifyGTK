#!/usr/bin/php-cgi

// Get the hash of the url
console.log(window.location.hash);
const hash = window.location.hash
    .substring(1)
    .split('&')
    .reduce(function (initial, item) {
        if (item) {
            var parts = item.split('=');
            initial[parts[0]] = decodeURIComponent(parts[1]);
        }
        return initial;
    }, {});
console.log(location.search);
const get = location.search
    .substring(1)
    .split('&')
    .reduce(function (initial, item) {
        if (item) {
            var parts = item.split('=');
            initial[parts[0]] = decodeURIComponent(parts[1]);
        }
        return initial;
    }, {});

window.location.hash = '';
// Set token
console.log(get.error)
let _error = get.error;
let _code = get.code;
let _token = hash.access_token;
let _expire = hash.expires_in;
let _refresh = hash.refresh_token;
let request_refresh = false;

const authEndpoint = 'https://accounts.spotify.com';

// Replace with your app's client ID, redirect URI and desired scopes
<?php
if (file_exists("../client-auth.txt")) {
    $file = file("../client-auth.txt");
    $clientId  = substr($file[0], 0, -1);
    $clientSecret  = substr($file[1], 0, -1);
    echo "const clientId = '" . $clientId . "';\n";
    echo "const clientSecret = '" . $clientSecret . "';\n";
}
?>
const redirectUri = 'http://localhost:8080/index.html';
const scopes = [
    'streaming',
    'user-read-email',
    'user-read-private'
];

<?php
echo "time_now = " . time() . ";\n";
if (file_exists("../token.txt")) {
    $file = file("../token.txt");
    $time_now = time();
    $expire_time = (int) substr($file[1], 0, -1);
    $refresh_token = substr($file[2], 0, -1);
    $token = substr($file[0], 0, -1);
    if ($expire_time > $time_now) {
        echo "_token = \"" . $token . "\";\n";
        echo "_expire = \"" . $expire_time . "\";\n";
        echo "_refresh = \"" . $refresh_token . "\";\n";
    } else {
        echo "request_refresh = true;";
    }
    //echo $expire_time . "-" . $time_now . " = " . $expire_time-$time_now;
}
?>

function saveToken(token, expiration, refresh_token) {
    var data = new FormData();
    data.append("token", token);
    data.append("expiration", expiration);
    data.append("refresh_token", refresh_token);
    var xhr = new XMLHttpRequest();
    xhr.open('post', 'save_backend.php', true);
    xhr.send(data);
}

if (_error) {
    msg = window.document.getElementById("initMessage");
    msg.style.color = "red";
    msg.textContent = _error;
    try_again = document.createElement("button");
    try_again.innerText = "Try again"
    try_again.onclick = function () {
        window.location = "/"
    }
    msg.parentNode.insertBefore(try_again, msg.nextSibling);
    console.log("Error received.");
} else if (request_refresh) {
    var b64 = btoa(`${clientId}:${clientSecret}`);
    fetch(`${authEndpoint}/api/token`, {
        method: 'POST',
        body: new URLSearchParams({
            'grant_type': 'refresh_token',
            'refresh_token': _refresh
        }),
        headers: {
            'Authorization': `Basic ${b64}`
        }
    }).then(res => res.json()).then(data => {
        _token = data.access_token;
        _expire = time_now + 3600;
        saveToken(_token, _expire, _refresh);
        console.log("Token saved.");
    });
} else if (_code) {
    // We have no error, but a code. So request a token now.
    var b64 = btoa(`${clientId}:${clientSecret}`);
    fetch(`${authEndpoint}/api/token`, {
        method: 'POST',
        body: new URLSearchParams({
            'grant_type': 'authorization_code',
            'code': _code,
            'redirect_uri': redirectUri
        }),
        headers: {
            'Authorization': `Basic ${b64}`
        }
    }).then(res => res.json()).then(data => {
        _token = data.access_token;
        _expire = data.expires_in;
        _refresh = data.refresh_token;
        saveToken(_token, _expire, _refresh);
        console.log("Token saved.");
    });
    history.replaceState(null, "", location.href.split("?")[0]);
} else if (_token) {

} else {
    window.location = `${authEndpoint}/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scopes.join('%20')}&response_type=code&show_dialog=false`;
}

window.onSpotifyWebPlaybackSDKReady = () => {
    const player = new Spotify.Player({
        name: 'SpotifyGTK',
        getOAuthToken: cb => {
            cb(_token);
        },
        volume: 0.5
    });
    // Ready
    player.addListener('ready', ({device_id}) => {
        console.log('Ready with Device ID', device_id);
        window.document.getElementById("togglePlay").disabled = false;
    });

    // Not Ready
    player.addListener('not_ready', ({device_id}) => {
        console.log('Device ID has gone offline', device_id);
        window.document.getElementById("initMessage").color = "red";
        window.document.getElementById("initMessage").textContent = "Device ID offline";
    });
    player.addListener('initialization_error', ({message}) => {
        console.error(message);
        window.document.getElementById("initMessage").color = "red";
        window.document.getElementById("initMessage").textContent = "Initialization error";
    });

    player.addListener('authentication_error', ({message}) => {
        console.error(message);
        window.document.getElementById("initMessage").color = "red";
        window.document.getElementById("initMessage").textContent = "Authentication error";
    });

    player.addListener('account_error', ({message}) => {
        console.error(message);
        window.document.getElementById("initMessage").color = "red";
        window.document.getElementById("initMessage").textContent = "Account error";
    });
    player.connect();
    document.getElementById('togglePlay').onclick = function () {
        player.togglePlay();
    };
}