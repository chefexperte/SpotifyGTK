function requestRefresh() {
    // noinspection JSUnresolvedVariable,JSDeprecatedSymbols
    let b64 = btoa(`${clientId}:${clientSecret}`);
    fetch(`${authEndpoint}/api/token`, {
        method: 'POST', body: new URLSearchParams({
            'grant_type': 'refresh_token', 'refresh_token': _refresh
        }), headers: {
            'Authorization': `Basic ${b64}`
        }
    }).then(res => res.json()).then(data => {
        // noinspection JSUnresolvedVariable,JSUndeclaredVariable
        _token = data.access_token;
        // noinspection JSUnresolvedVariable
        let expire = 3600;
        // noinspection JSUndeclaredVariable
        _expire = Math.round(Date.now()/1000);
        saveToken(_token, expire, _refresh).then();
        console.log("Token saved.");
    });
    request_refresh = false;
    console.log("Refresh done.")
}