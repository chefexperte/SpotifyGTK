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
window.location.hash = '';
// Set token
let _token = hash.access_token;

const authEndpoint = 'https://accounts.spotify.com/authorize';

// Replace with your app's client ID, redirect URI and desired scopes
const clientId = 'PUT IT HERE';
const redirectUri = 'http://localhost:8080/index.html';
const scopes = [
    'streaming',
    'user-read-email',
    'user-read-private'
];

function saveToken(text) {
    var data = new FormData();
    data.append("data", text);
    var xhr = new XMLHttpRequest();
    xhr.open('post', 'save_backend.php', true);
    xhr.send(data);
}

// If there is no token, redirect to Spotify authorization
if (!_token) {
    window.location = `${authEndpoint}?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scopes.join('%20')}&response_type=token&show_dialog=true`;
} else {
    saveToken(_token);
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
    });

    // Not Ready
    player.addListener('not_ready', ({device_id}) => {
        console.log('Device ID has gone offline', device_id);
    });
    player.addListener('initialization_error', ({message}) => {
        console.error(message);
    });

    player.addListener('authentication_error', ({message}) => {
        console.error(message);
    });

    player.addListener('account_error', ({message}) => {
        console.error(message);
    });
    player.connect();
    document.getElementById('togglePlay').onclick = function () {
        player.togglePlay();
    };
}