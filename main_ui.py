import os

import gi

from playback_info import PlaybackInfo
from thread_tools.delayed_thread import DelayedThread

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw


class SpotifyGtkUI:
    play_button: Gtk.Button = None
    next_button: Gtk.Button = None
    previous_button: Gtk.Button = None
    position_slider: Gtk.Scale = None
    loudness_slider: Gtk.Scale = None
    track_title: Gtk.Label = None
    loading_box: Gtk.Box = None
    main_box: Gtk.Box = None
    overlay_container: Gtk.Overlay = None
    callbacks: [()] = None
    volume_change_delay: DelayedThread = None
    position_change_delay: DelayedThread = None
    play_state_change_delay: DelayedThread = None
    track_duration: int = None
    is_playing = False
    device_ready = False
    controllable_widgets: [Gtk.Widget] = None
    loading_label: Gtk.Label = None

    def __init__(self):
        self.file_dir = os.path.dirname(os.path.abspath(__file__))
        self.app = Adw.Application(application_id='de.flxtea.spotify')
        man = Adw.StyleManager.get_default()
        man.set_color_scheme(Adw.ColorScheme.PREFER_DARK)
        self.controllable_widgets = []

    def on_activate(self, appl):
        global css_provider
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(self.file_dir + "/style.css")
        win = Adw.ApplicationWindow(application=appl)
        win.css_provider = css_provider
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        headerbar = Gtk.HeaderBar()
        play_here_button = Gtk.Button(icon_name="computer-symbolic")
        play_here_button.connect("clicked", self.play_here)
        headerbar.pack_end(play_here_button)

        upper_box = Gtk.Box()
        upper_box.add_css_class("toolbar")
        upper_box.add_css_class("osd")

        upper_box.set_margin_bottom(15)
        upper_box.set_margin_start(15)
        upper_box.set_margin_end(15)
        upper_box.set_margin_top(15)
        self.track_title = Gtk.Label(label="Loading...")
        upper_box.append(self.track_title)
        player_box = Gtk.Box()
        player_box.add_css_class("toolbar")
        player_box.add_css_class("osd")
        player_box.set_vexpand(True)
        player_box.set_valign(Gtk.Align.END)
        player_box.set_margin_bottom(15)
        player_box.set_margin_start(15)
        player_box.set_margin_end(15)
        player_box.set_margin_top(15)
        player_box.set_size_request(500, 0)
        player_controls = Gtk.Box()
        player_controls.add_css_class("linked")
        self.previous_button = Gtk.Button(icon_name="media-skip-backward-symbolic")
        self.play_button = Gtk.Button(icon_name="media-playback-pause-symbolic")
        self.play_button.connect("clicked", self.toggle_play)
        self.play_button.set_sensitive(False)
        self.next_button = Gtk.Button(icon_name="media-skip-forward-symbolic")
        self.play_button.add_css_class("circular")
        self.previous_button.add_css_class("circular")
        self.next_button.add_css_class("circular")
        player_controls.append(self.previous_button)
        player_controls.append(self.play_button)
        player_controls.append(self.next_button)
        player_box.append(player_controls)
        self.position_slider = Gtk.Scale()
        self.position_slider.set_range(0, 100)
        self.position_slider.set_hexpand(True)
        self.position_slider.set_value(0)
        self.position_slider.connect("change-value", lambda a, b, c: self.position_change())
        player_box.append(self.position_slider)
        volume_button_box = Gtk.EventControllerMotion()
        volume_button = Gtk.Button(icon_name="audio-volume-high")
        context = volume_button.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        volume_button.add_controller(volume_button_box)
        volume_button.add_css_class("circular")
        volume_button.add_css_class("fadeout")
        volume_button.set_vexpand(False)
        volume_button.set_can_focus(False)
        fixed = Gtk.Fixed()
        fixed.set_valign(Gtk.Align.CENTER)
        self.loudness_slider = Gtk.Scale()
        self.loudness_slider.set_inverted(True)
        self.loudness_slider.set_range(0, 100)
        self.loudness_slider.set_hexpand(False)
        self.loudness_slider.set_value(100)
        self.loudness_slider.add_css_class("fadein")
        self.loudness_slider.connect("value-changed", lambda a: self.volume_change())
        # volume_button_box.connect("enter", lambda a, b, c: fade_in(fixed, volume_button, self.loudness_slider))
        # volume_button_box.connect("leave", lambda a: fade_out(fixed, volume_button, self.loudness_slider))
        # fixed.put(loudness_slider, 0, 0)
        # fixed.put(volume_button, 0, 0)
        # player_box.append(fixed)
        player_box.append(self.loudness_slider)

        # Main box contains all content besides the headerbar
        self.main_box.append(upper_box)
        self.main_box.append(player_box)
        self.main_box.set_hexpand(True)
        self.main_box.set_vexpand(True)

        self.overlay_container = Gtk.Overlay()
        # self.overlay_container.set_size_request(600, 300)
        self.overlay_container.set_hexpand(True)
        self.overlay_container.set_vexpand(True)
        # self.overlay_container.set_halign(Gtk.Align.CENTER)
        # self.overlay_container.set_valign(Gtk.Align.CENTER)
        self.overlay_container.set_child(self.main_box)

        self.loading_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.loading_box.set_hexpand(True)
        self.loading_box.set_vexpand(True)
        self.loading_box.set_halign(Gtk.Align.CENTER)
        self.loading_box.set_valign(Gtk.Align.CENTER)
        self.main_box.add_css_class("blur")
        spinner = Gtk.Spinner()
        spinner.set_size_request(50, 50)
        spinner.start()
        self.loading_label = Gtk.Label(label="Loading...")
        self.loading_box.append(spinner)
        self.loading_box.append(self.loading_label)

        self.overlay_container.add_overlay(self.loading_box)
        # self.overlay_container.add_overlay(self.main_box)

        # Window Box contains headerbar + everything else(self.main_box)
        window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        window_box.append(headerbar)
        window_box.append(self.overlay_container)

        win.set_content(window_box)

        add_styling({window_box})

        win.connect("close-request", lambda x: win.destroy())
        win.set_title("SpotifyGTK")

        self.controllable_widgets.append(self.play_button)
        self.controllable_widgets.append(self.position_slider)
        self.controllable_widgets.append(self.loudness_slider)
        self.controllable_widgets.append(self.next_button)
        self.controllable_widgets.append(self.previous_button)
        for widget in self.controllable_widgets:
            if widget is None:
                print(str(widget) + " is None.")
                continue
            widget.set_sensitive(False)

        win.present()

    def backend_ready_callback(self):
        for widget in self.controllable_widgets:
            widget.set_sensitive(True)
        self.main_box.remove_css_class("blur")
        self.overlay_container.remove_overlay(self.loading_box)
        self.device_ready = True

    def report_state_callback(self, info: PlaybackInfo):
        self.track_duration = info.duration
        percent = 0
        if info.duration != 0:
            percent = (info.position / info.duration) * 100
        if not self.position_change_delay or not self.position_change_delay.is_running():
            self.position_slider.set_value(percent)
        self.track_title.set_text(info.title)
        if info.playing:
            if self.play_state_change_delay is None or not self.play_state_change_delay.is_running():
                self.play_button.set_icon_name("media-playback-pause-symbolic")
            self.is_playing = True
        else:
            if self.play_state_change_delay is None or not self.play_state_change_delay.is_running():
                self.play_button.set_icon_name("media-playback-start-symbolic")
            self.is_playing = False

    def toggle_play(self, d):
        self.is_playing = not self.is_playing
        if self.play_state_change_delay is None or not self.play_state_change_delay.is_running():
            self.play_state_change_delay = DelayedThread(None, [], 300)
            if self.is_playing:
                self.play_button.set_icon_name("media-playback-pause-symbolic")
            else:
                self.play_button.set_icon_name("media-playback-start-symbolic")
        self.callbacks["toggle_play"](d)

    def position_change(self):
        if self.position_change_delay is not None and self.position_change_delay.is_running():
            self.position_change_delay.args = [self.position_slider.get_value() / 100 * self.track_duration]
        else:
            self.position_change_delay = \
                DelayedThread(self.callbacks["set_position"],
                              [self.position_slider.get_value() / 100 * self.track_duration], 300)

    def volume_change(self):
        if self.volume_change_delay is not None and self.volume_change_delay.is_running():
            self.volume_change_delay.args = [self.loudness_slider.get_value()]
        else:
            self.volume_change_delay = \
                DelayedThread(self.callbacks["set_volume"], [self.loudness_slider.get_value()], 200)

    def play_here(self, d):
        self.callbacks["play_here"]()

    def run_ui(self, callbacks):
        self.callbacks = callbacks
        self.app.connect('activate', self.on_activate)
        try:
            self.app.run(None)
        except KeyboardInterrupt:
            pass


css_provider = None


def add_styling(widget):
    global css_provider
    for widget in widget:
        context = widget.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        add_styling(widget)
