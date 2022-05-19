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

const redirectUri = 'http://localhost:8080/get_auth.html';
const scopes = [
    'streaming',
    'user-read-email',
    'user-read-private',
    'app-remote-control',
    'user-read-playback-state',
    'user-modify-playback-state'
];
const authEndpoint = 'https://accounts.spotify.com';

_login = get.login;

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

async function saveToken(token, expiration, refresh_token) {
    if (!token || !expiration || !refresh_token) return;
    let data = new FormData();
    data.append("token", token);
    data.append("expiration", expiration);
    data.append("refresh_token", refresh_token);
    let xhr = new XMLHttpRequest();
    await xhr.open('post', 'save_backend.php', false);
    await xhr.send(data);
}


if (_login) {
    console.log("Redirecting to WebPlayer")
    document.getElementById("initMessage").innerText = "Login success.";
    window.location = "/index.html";
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
    console.log("Refreshing...")
    requestRefresh();
    //window.location = "/get_auth.html?login=true";
} else if (_code) {
    // We have no error, but a code. So request a token now.
    // noinspection JSUnresolvedVariable,JSDeprecatedSymbols
    let b64 = btoa(`${clientId}:${clientSecret}`);
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
    }).then(res => res.json()).then(async data => {
        // noinspection JSUnresolvedVariable,JSUndeclaredVariable
        _token = data.access_token;
        // noinspection JSUnresolvedVariable,JSUndeclaredVariable
        _expire = data.expires_in;
        // noinspection JSUndeclaredVariable
        _refresh = data.refresh_token;
        await saveToken(_token, _expire, _refresh);
        console.log(_token);
        console.log(_expire);
        console.log(_refresh);
        console.log("Token saved.")
        window.location = "/get_auth.html?login=true";
        //console.log("GO TO INDEX HTML")
    });
    history.replaceState(null, "", location.href.split("?")[0]);
} else if (_token) {
    //everything is ready
    document.getElementById("initMessage").innerText = "Login success.";
    window.location = "/index.html";
    //console.log("TOKEN IST DA");
} else {
    // noinspection JSUnresolvedVariable
    window.location = `${authEndpoint}/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scopes.join('%20')}&response_type=code&show_dialog=false`;
}