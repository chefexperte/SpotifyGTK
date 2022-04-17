// Get the hash of the url
console.log(window.location.hash);
const hash = window.location.hash
    .substring(1)
    .split('&')
    .reduce(function (initial, item) {
        if (item) {
            let parts = item.split('=');
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
            let parts = item.split('=');
            initial[parts[0]] = decodeURIComponent(parts[1]);
        }
        return initial;
    }, {});

window.location.hash = '';
// Set token
console.log(get.error)

if (typeof _error === 'undefined') {
    _error = get.error;
}
if (typeof _code === 'undefined') {
    _code = get.code;
}
if (typeof _token === 'undefined') {
    // noinspection JSUnresolvedVariable
    _token = hash.access_token;
}
if (typeof _expire === 'undefined') {
    // noinspection JSUnresolvedVariable
    _expire = hash.expires_in;
}
if (typeof _refresh === 'undefined') {
    _refresh = hash.refresh_token;
}
if (typeof request_refresh === 'undefined') {
    request_refresh = false;
}

let isReady = false;

const authEndpoint = 'https://accounts.spotify.com';
const apiEndpoint = 'https://api.spotify.com/v1';


const redirectUri = 'http://localhost:8080/index.html';
const scopes = [
    'streaming',
    'user-read-email',
    'user-read-private',
    'app-remote-control',
    'user-read-playback-state',
    'user-modify-playback-state'
];

function setReady(ready) {
    if (isReady && !ready) {
        //state change from ready to not ready
        isReady = false;
        window.document.getElementById("setVolume").disabled = true;
        window.document.getElementById("playHere").disabled = true;
        window.document.getElementById("togglePlay").disabled = true;
        window.document.getElementById("setPosition").disabled = true;
    } else if (!isReady && ready) {
        //state change from not ready to ready
        isReady = true;
        window.document.getElementById("setVolume").disabled = false;
        window.document.getElementById("playHere").disabled = false;
        window.document.getElementById("togglePlay").disabled = false;
        window.document.getElementById("setPosition").disabled = false;
    }
}

function saveToken(token, expiration, refresh_token) {
    if (!token || !expiration || !refresh_token) return;
    let data = new FormData();
    data.append("token", token);
    data.append("expiration", expiration);
    data.append("refresh_token", refresh_token);
    let xhr = new XMLHttpRequest();
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
    // noinspection JSUnresolvedVariable
    let b64 = btoa(`${clientId}:${clientSecret}`);
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
        // noinspection JSUnresolvedVariable
        _token = data.access_token;
        // noinspection JSUnresolvedVariable
        let expire = 3600;
        saveToken(_token, expire, _refresh);
        console.log("Token saved.");
    });
} else if (_code) {
    // We have no error, but a code. So request a token now.
    // noinspection JSUnresolvedVariable
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
        // noinspection JSUnresolvedVariable
        _token = data.access_token;
        // noinspection JSUnresolvedVariable
        _expire = data.expires_in;
        _refresh = data.refresh_token;
        saveToken(_token, _expire, _refresh);
        console.log("Token saved.");
    });
    history.replaceState(null, "", location.href.split("?")[0]);
} else if (_token) {
    //everything is ready
} else {
    // noinspection JSUnresolvedVariable
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
        setReady(true);
        document.getElementById('togglePlay').onclick = function () {
            player.getCurrentState().then(state => {
                if (!state) {
                    // User is not playing music through the Web Playback SDK
                    // fetch if currently playing or not
                    fetch(`${apiEndpoint}/me/player`, {
                        method: 'GET',
                        headers: {
                            'Authorization': `Bearer ${_token}`
                        }
                    }).then(res => res.json()).then(data => {
                        // noinspection JSUnresolvedVariable
                        let curr_id = data.device.id;
                        // noinspection JSUnresolvedVariable
                        let playing = data.is_playing;
                        // if is playing, pause
                        if (playing) {
                            fetch(`${apiEndpoint}/me/player/pause`, {
                                method: 'PUT',
                                headers: {
                                    'Authorization': `Bearer ${_token}`
                                }
                            });
                        } else {
                            //if not playing, play
                            fetch(`${apiEndpoint}/me/player/play`, {
                                method: 'PUT',
                                headers: {
                                    'Authorization': `Bearer ${_token}`
                                }
                            });
                        }
                    });
                } else {
                    player.togglePlay();
                }
            });
        };
        document.getElementById('playHere').onclick = function () {
            setReady(false)
            let json_data = JSON.stringify({device_ids: [device_id]});
            fetch(`${apiEndpoint}/me/player`, {
                method: 'PUT',
                body: json_data,
                headers: {
                    'Authorization': `Bearer ${_token}`
                }
            }).then(() => {
                setReady(true);
            });
        };
        // setting playback volume
        document.getElementById('setVolume').onclick = function () {
            let volume = document.getElementById("volume").value; // get volume
            volume = Math.max(Math.min(100, volume), 0); // limit to value between 0 and 100
            // var json_data = JSON.stringify({volume_percent: volume});
            player.getCurrentState().then(state => {
                if (!state) {
                    fetch(`${apiEndpoint}/me/player/volume?volume_percent=${volume}`, {
                        method: 'PUT',
                        headers: {
                            'Authorization': `Bearer ${_token}`,
                            'Content-Type': 'application/json'
                        }
                    }).then();
                } else {
                    player.setVolume(volume / 100)
                }
            });
        };
        // setting playback position
        document.getElementById('setPosition').onclick = function () {
            let position = document.getElementById("playbackPosition").value; // get volume
            player.getCurrentState().then(state => {
                if (!state) {
                    //TODO
                } else {
                    player.seek(position);
                    document.getElementById("position").innerText = position
                }
            });

        };
        let timer;
        let reportState = function () {
            player.getCurrentState().then(state => {
                if (!state) {
                    // We're not playing music
                    return;
                }
                document.getElementById("position").innerText = state.position;
                document.getElementById("trackDuration").innerText = state.duration;
            });
            timer = setTimeout(reportState, 1000);
        };
        reportState();


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
}