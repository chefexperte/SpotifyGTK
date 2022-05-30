import os

import gi

import static_strings as ss
import tools.data_tools
from tools.data_wrapper import TrackData, PlaybackInfo, DataWithImage
from special_widgets import ArtistButton
from thread_tools.delayed_thread import DelayedThread

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GdkPixbuf, GLib


class SpotifyGtkUI:
	play_button: Gtk.Button = None
	next_button: Gtk.Button = None
	previous_button: Gtk.Button = None
	position_slider: Gtk.Scale = None
	loudness_slider: Gtk.Scale = None
	upper_box: Gtk.Box = None
	track_title: Gtk.Button = None
	track_artists: Gtk.Box = None
	track_image: Gtk.Image = None
	loading_box: Gtk.Box = None
	main_box: Gtk.Box = None
	overlay_container: Gtk.Overlay = None
	loading_spinner: Gtk.Spinner = None
	loading_label: Gtk.Label = None
	leaflet_container: Adw.Leaflet = None
	artist_page: Gtk.Box = None

	callbacks: [()] = None
	volume_change_delay: DelayedThread = None
	position_change_delay: DelayedThread = None
	play_state_change_delay: DelayedThread = None
	track_duration: int = None
	is_playing = False
	device_ready = False
	controllable_widgets: [Gtk.Widget] = None

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

		# Upper part
		self.upper_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		self.upper_box.add_css_class("toolbar")
		self.upper_box.add_css_class("osd")
		self.upper_box.set_margin_bottom(20)
		self.upper_box.set_margin_start(15)
		self.upper_box.set_margin_end(15)
		self.upper_box.set_margin_top(20)
		self.track_title = Gtk.Button(label="Loading...")
		self.track_title.add_css_class("track_title")
		self.track_title.add_css_class("flat")
		self.track_title.set_hexpand(False)
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=ss.image_cache + ".no_album", width=200, height=200,
		                                                 preserve_aspect_ratio=True)
		self.track_image = Gtk.Image.new_from_pixbuf(pixbuf)
		self.track_image.set_vexpand(True)
		self.track_image.set_margin_start(-5)
		# self.track_image.set_hexpand(True)
		self.track_image.set_size_request(100, 100)
		self.upper_box.append(self.track_image)
		title_artist_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		title_box = Gtk.Box()
		title_box.set_hexpand(False)
		title_box.append(self.track_title)
		title_artist_box.append(title_box)
		self.track_artists = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		# self.track_artists.append(Gtk.Button(label="ARTIST 1"))
		title_artist_box.append(self.track_artists)
		self.upper_box.append(title_artist_box)

		# Playback bar
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
		# player_controls.add_css_class("linked")
		player_controls.add_css_class("osd")
		player_controls.add_css_class("round")
		player_controls.set_margin_top(5)
		player_controls.set_margin_bottom(5)
		self.previous_button = Gtk.Button(icon_name="media-skip-backward-symbolic")
		self.previous_button.connect("clicked", self.skip_previous)
		self.play_button = Gtk.Button(icon_name="media-playback-pause-symbolic")
		self.play_button.connect("clicked", self.toggle_play)
		self.next_button = Gtk.Button(icon_name="media-skip-forward-symbolic")
		self.next_button.connect("clicked", self.skip_next)

		self.play_button.add_css_class("play-button")
		self.play_button.add_css_class("no-vert-padding")
		self.play_button.set_size_request(40, 40)
		self.previous_button.add_css_class("no-vert-padding")
		self.previous_button.set_size_request(40, 40)
		self.next_button.add_css_class("no-vert-padding")
		self.next_button.set_size_request(40, 40)

		self.play_button.add_css_class("circular")
		self.play_button.add_css_class("raised")
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
		player_box.append(self.loudness_slider)

		# Artist page
		self.artist_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		artist_page_headerbar = Gtk.HeaderBar()
		go_back_button = Gtk.Button(icon_name="go-previous-symbolic")
		go_back_button.connect("clicked", lambda d: self.leaflet_container.navigate(Adw.NavigationDirection.BACK))
		artist_page_headerbar.pack_start(go_back_button)
		self.artist_page.append(artist_page_headerbar)
		self.artist_page.append(Gtk.Label(label="Artist page"))

		# Main box contains all content besides the headerbar
		self.main_box.append(self.upper_box)
		self.main_box.append(player_box)
		self.main_box.set_hexpand(True)
		self.main_box.set_vexpand(True)

		# Overlay container for loading screen
		self.overlay_container = Gtk.Overlay()
		self.overlay_container.set_hexpand(True)
		self.overlay_container.set_vexpand(True)
		self.overlay_container.set_child(self.main_box)

		self.loading_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.loading_box.set_hexpand(True)
		self.loading_box.set_vexpand(True)
		self.loading_box.set_halign(Gtk.Align.CENTER)
		self.loading_box.set_valign(Gtk.Align.CENTER)
		self.main_box.add_css_class("blur")
		self.loading_spinner = Gtk.Spinner()
		self.loading_spinner.set_size_request(50, 50)
		self.loading_spinner.start()
		self.loading_label = Gtk.Label(label="Loading...")
		self.loading_box.append(self.loading_spinner)
		self.loading_box.append(self.loading_label)

		self.overlay_container.add_overlay(self.loading_box)

		# Window Box contains headerbar + everything else(self.main_box)
		window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		window_box.append(headerbar)
		window_box.append(self.overlay_container)

		self.leaflet_container = Adw.Leaflet()
		self.leaflet_container.set_can_navigate_back(True)
		self.leaflet_container.set_can_unfold(False)
		self.leaflet_container.append(window_box)
		self.leaflet_container.append(self.artist_page)

		win.set_content(self.leaflet_container)

		add_styling({self.leaflet_container})

		win.connect("close-request", lambda x: win.destroy())
		win.set_title("SpotifyGTK")

		self.controllable_widgets.append(self.play_button)
		self.controllable_widgets.append(self.position_slider)
		self.controllable_widgets.append(self.loudness_slider)
		self.controllable_widgets.append(self.next_button)
		self.controllable_widgets.append(self.previous_button)
		self.controllable_widgets.append(self.track_title)
		self.controllable_widgets.append(self.track_artists)
		for widget in self.controllable_widgets:
			if widget is None:
				print(str(widget) + " is None.")
				continue
			widget.set_sensitive(False)

		win.present()

	def backend_ready_callback(self):
		def f(): GLib.idle_add(self.backend_ready)
		DelayedThread(f, [], 400)
		self.update_loading_message("Ready!")
		self.loading_spinner.stop()

	def backend_ready(self):
		def set_ready():
			self.track_title.set_label("No song loaded.")
			for widget in self.controllable_widgets:
				widget.set_sensitive(True)
			self.main_box.remove_css_class("blur")
			self.overlay_container.remove_overlay(self.loading_box)
			self.device_ready = True
		GLib.idle_add(set_ready)

	def report_state_callback(self, info: PlaybackInfo):
		self.track_duration = info.duration
		percent = 0
		if info.duration != 0:
			percent = (info.position / info.duration) * 100
		if not self.position_change_delay or not self.position_change_delay.is_running():
			self.position_slider.set_value(percent)
		# Since we're now doing this with get_track_info() I think we could remove this
		# self.track_title.set_label(info.title)
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

	def update_loading_message(self, message: str):
		self.loading_label.set_text(message)

	def get_track_info(self, track_info: TrackData):
		def set_data():
			self.track_title.set_label(track_info.name)
			had_child = True
			while had_child is True:
				had_child = False
				# noinspection PyTypeChecker
				for child in self.track_artists:
					self.track_artists.remove(child)
					had_child = True
			for artist in track_info.artists:
				artist_button = Gtk.Button(label=artist.name)
				artist_button.connect("clicked", lambda d: self.leaflet_container.navigate(Adw.NavigationDirection.FORWARD))
				artist_button.set_margin_start(5)
				self.track_artists.append(artist_button)
		GLib.idle_add(set_data)
		print("New track data loaded")
		file_name = track_info.get_image()
		if file_name is not None:
			def set_image():
				pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=file_name, width=200, height=200,
				                                                 preserve_aspect_ratio=True)
				self.track_image.set_from_pixbuf(pixbuf)
			GLib.idle_add(set_image)
			print("New image set")
		else:
			print("Could not load file :(")

	def skip_next(self, d):
		self.callbacks["skip_next"]()

	def skip_previous(self, d):
		self.callbacks["skip_previous"]()

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
