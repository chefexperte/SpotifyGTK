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

//const authEndpoint = 'https://accounts.spotify.com';
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

let extPlayerData = null;

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
} else if (_token) {
    // everything is ready
} else {
    // go to the login script
    window.location = `get_auth.html`;
}

function getExternalPlayerData() {
    return fetch(`${apiEndpoint}/me/player`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${_token}`
        }
    }).then(res => {
        if (res.status === 204) return;
        return res.json().then(data => {
            // console.log(data)
            return data;
        })
    });
}

function togglePlay(player) {
    player.getCurrentState().then(state => {
        if (!state) {
            // User is not playing music through the Web Playback SDK
            // fetch if currently playing or not
            if (extPlayerData == null) return;
            // noinspection JSUnresolvedVariable
            let playing = extPlayerData.is_playing;
            // if player is playing, pause
            if (playing) {
                fetch(`${apiEndpoint}/me/player/pause`, {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${_token}`
                    }
                }).then();
            } else {
                //if not playing, play
                fetch(`${apiEndpoint}/me/player/play`, {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${_token}`
                    }
                }).then();
            }
        } else {
            player.togglePlay();
        }
    });
}

function playHere(device_id) {
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
}

function setVolume(player) {
    let volume = document.getElementById("volume").value; // get volume
    volume = Math.max(Math.min(100, volume), 0); // limit to value between 0 and 100
    // var json_data = JSON.stringify({volume_percent: volume});
    player.getCurrentState().then(state => {
        if (!state) {
            // noinspection JSUnresolvedVariable
            if (extPlayerData == null || extPlayerData.device == null) return;
            let device_id = extPlayerData.device.id;
            fetch(`${apiEndpoint}/me/player/volume?volume_percent=${volume}&device_id=${device_id}`, {
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
}

function setPosition(player) {
    let position = document.getElementById("playbackPosition").value; // get volume
    player.getCurrentState().then(state => {
        if (!state) {
            document.getElementById("position").innerText = position
            // noinspection JSUnresolvedVariable
            //if (extPlayerData == null || extPlayerData.device == null) return;
            //let device_id = extPlayerData.device.id;
            fetch(`${apiEndpoint}/me/player/seek?position_ms=${position}`, {//&device_id=${device_id}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${_token}`,
                    'Content-Type': 'application/json'
                }
            }).then();
        } else {
            player.seek(position);
            document.getElementById("position").innerText = position
        }
    });
}

function setMediaInformation(title, artist) {
    if ('mediaSession' in navigator) {
        navigator.mediaSession.metadata = new MediaMetadata({
            title: title,
            artist: artist,
            //album: 'Whenever You Need Somebody'
        });
    }
    navigator.mediaSession.playbackState = "playing"
    //TODO
}

window.onSpotifyWebPlaybackSDKReady = () => {
    // noinspection JSUnusedGlobalSymbols
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
            togglePlay(player);
        };
        document.getElementById('playHere').onclick = function () {
            playHere(device_id);
        };
        // setting playback volume
        document.getElementById('setVolume').onclick = function () {
            setVolume(player)
        };
        // setting playback position
        document.getElementById('setPosition').onclick = function () {
            setPosition(player)
        };
        // report state loop will put information on the page every second
        let timer;
        let name, position, duration, isPlaying;
        let reportState = async function () {
            let next_report = 1000;
            await player.getCurrentState().then(async state => {
                if (!state) {
                    // We're not playing music in the webplayer
                    await getExternalPlayerData().then(data => {
                        extPlayerData = data
                    });
                    if (extPlayerData == null) return;
                    if (extPlayerData.item != null) {
                        name = extPlayerData.item.name;
                        // noinspection JSUnresolvedVariable
                        duration = extPlayerData.item.duration_ms;
                    }
                    // noinspection JSUnresolvedVariable
                    position = extPlayerData.progress_ms;
                    // noinspection JSUnresolvedVariable
                    isPlaying = extPlayerData.is_playing;
                    next_report = 1000;
                } else {
                    isPlaying = !state.paused;
                    // noinspection JSUnresolvedVariable
                    name = state.track_window.current_track.name
                    position = state.position;
                    duration = state.duration;
                    next_report = 800;
                }
            });
            document.title = name;
            document.getElementById("trackTitle").innerText = name;
            document.getElementById("position").innerText = position;
            document.getElementById("trackDuration").innerText = duration;
            document.getElementById("isPlaying").innerText = isPlaying;

            setMediaInformation(name, "TODO");

            timer = setTimeout(reportState, next_report);
        };
        reportState().then();


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