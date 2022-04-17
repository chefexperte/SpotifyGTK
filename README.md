# SpotifyGTK

Currently there is not much to see yet, but this is supposed to be a Spotify player with a modern GTK/Libadwaita interface. 

https://user-images.githubusercontent.com/12102112/163695312-6972c397-a646-4398-ba02-9986050ce15a.mp4

# How does it work?
Or rather will work when it's done. 
SpotifyGTK, as I do plan at the moment will have three main components. 
1. The UI, written in Gtk 4.0 and Libadwaita 1.0, which is what you will see as a user. Playing songs, browsing Spotify, and so on. 
2. The webserver, using http.server and a CGIHTTPRequestHandler. It does handle HTML/CSS/JS/PHP (for now), 
and is supposed to run a minimalistic web implementation of the Spotify Web Playback SDK to play full songs, instead of the 30s previews.
3. An invisible instance of a browser, for now I have been trying to use Firefox, controlled by selenium. This will be the connection between
the webserver and the UI. Spotify does not directly allow loading audio, because it wants to use DRM, so we must use a browser and one that 
also supports Widevine CDM for DRM. 


# Requirements
To use most of the features you need a Spotify Premium account. 
For running the browser control using Selenium you need to put the geckodriver executable in the directory of web.py. You can get it here:
[Mozilla Geckodriver](https://github.com/mozilla/geckodriver/releases)
Haven't tested it, but the UI should need Libadwaita and Gtk 4 support
Python packages used: PyGObject, selenium, pydbus

# What can I run/try yet?
For now you can:
## Browser Control with Selenium
Start web.py with one or two arguments, first one being your email address, second one being your password. If you only give it your 
mail it will ask for you password as input next. It will start Firefox using Geckodriver, log you in automatically, go to the Spotify Webplayer and replace 
the body with a song embed. Because you are on a secure source domain and you are logged in, you should be able to listen to the full song from the embed, 
instead of the 30s preview
## Webserver with Spotify authorization
Start webserver.py and you can use the webapp from localhost:8080 (you can also change that). It will ask for authorization
from the Spotify page and give the webapp a token, which enables you to start playing your music from the webapp, which will show up as a device on other Spotify 
devices as well. 
## The UI
Start main.py and it will launch the UI, which currently only has a player toolbar on the bottom without functionality, but it works. 
**UPDATE:** I have now added a small working version. 
When you start main.py, it will launch the server, the controller and the ui. 

The server is for handling HTML, JS, PHP, loading the Spotify Web Playback SDK and playback. The controller will log you in, grant auth, and allow you to start your previous playing song over the play button in the ui. 
