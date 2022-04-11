// Get the hash of the url
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
let _token = hash.access_token;
let _expire = hash.expires_in;
let _refresh = hash.refresh_token;

const authEndpoint = 'https://accounts.spotify.com/authorize';

// Replace with your app's client ID, redirect URI and desired scopes
const clientId = 'PUT IT HERE';
const redirectUri = 'http://localhost:8080/index.html';
const scopes = [
    'streaming',
    'user-read-email',
    'user-read-private'
];

function saveToken(token, expiration, refresh_token) {
    var data = new FormData();
    data.append("token", token);
    data.append("expiration", expiration);
    data.append("refresh_token", refresh_token);
    var xhr = new XMLHttpRequest();
    xhr.open('post', 'save_backend.php', true);
    xhr.send(data);
}

// If there is no token, redirect to Spotify authorization
if (!_token && !_error) {
    window.location = `${authEndpoint}?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scopes.join('%20')}&response_type=token&show_dialog=true`;
} else {
    if (!_error) {
        saveToken(_token, _expire, _refresh);
        console.log("Token saved.");
    } else {
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
    }

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