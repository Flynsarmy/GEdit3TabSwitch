# -*- coding: utf-8 -*-

from gi.repository import GObject, Gtk, Gdk, Gedit, PeasGtk, Pango

import pickle, os

class GEdit3TabSwitch(GObject.Object, Gedit.WindowActivatable, PeasGtk.Configurable):
    window = GObject.property(type=Gedit.Window)

    SETTINGS_FILENAME = "settings.pkl"
    
    tab_switch_leftright_default=True

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        handlers = []
        handler_id = self.window.connect('key-press-event', self.on_key_press_event)
        handlers.append(handler_id)
        self.window.GEdit3TabSwitchHandlers = handlers

    def do_deactivate(self):
        handlers = self.window.GEdit3TabSwitchHandlers
        for handler_id in handlers:
            self.window.disconnect(handler_id)

    def do_update_state(self):
        pass

    def do_create_configure_widget(self):
        """Create and display configuration widget."""
        widget = Gtk.VBox(3)
        self.load()
        button1 = Gtk.RadioButton(label="Press [Tab] for switching through last _used tabs", use_underline=True)
        button2 = Gtk.RadioButton(group= button1, label="Press [Tab] for switching through _right/left tabs", use_underline=True)
        widget.set_border_width(6)
        title_label = Gtk.Label("Tab switching")
        Gtk.Widget.modify_font(title_label, Pango.font_description_from_string("14"))
        widget.add(title_label)
        widget.add(button1)
        widget.add(button2)
        return widget

    def load(self):
        """Loads language settings."""
        settings_path = self.get_path()
        if os.path.exists(settings_path):
            try:
                settings_file = open(settings_path, "rb")
            except IOError:
                print("Failed to load settings.")
            self.tab_switch_leftright_default = pickle.load(settings_file)
            settings_file.close()

    def save(self):
        """Saves language settings."""
        settings_path = self.get_path()
        try:
            settings_file = open(settings_path, "wb")
        except IOError:
            print("Failed to open the settings file.")
        pickle.dump(self.tab_switch_leftright_default, settings_file)
        settings_file.close()

    def get_path(self):
        """Returns the settings file path."""
        path = os.path.abspath(os.path.dirname (__file__))
        path += os.path.sep
        return path + self.SETTINGS_FILENAME

    def on_key_press_event(self, window, event):
        key = Gdk.keyval_name(event.keyval)

        if event.state & Gdk.ModifierType.CONTROL_MASK and key in ('Tab', 'ISO_Left_Tab'):
            atab = window.get_active_tab()
            tabs = atab.get_parent().get_children()
            tlen = len(tabs)
            i = 0
            tab = atab

            for tab in tabs:
                i += 1
                if tab == atab:
                    break

            if key == 'ISO_Left_Tab':
                i -= 2

            if i < 0:
                tab = tabs[tlen-1]
            elif i >= tlen:
                tab = tabs[0]
            else:
                tab = tabs[i]

            window.set_active_tab(tab)

            return True
