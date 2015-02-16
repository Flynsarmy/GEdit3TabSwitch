# -*- coding: utf-8 -*-
"""
Author: Georg Schlagholz
https://github.com/Flynsarmy/GEdit3TabSwitch
plugin for gedit
need corresponding plugin file
"""
from gi.repository import GObject, Gtk, Gdk, Gedit, PeasGtk, Pango

import pickle, os

class GEdit3TabSwitch(GObject.Object, Gedit.WindowActivatable, PeasGtk.Configurable):
    """ 
Main plugin class. init and activate initialises the plugin
Switches tabs of gedit via shortcuts."""

    bool = None
    window = GObject.property(type=Gedit.Window)

    SETTINGS_FILENAME = "settings.pkl"
    
    tab_switch_leftright_default = True

    def __init__(self):
        GObject.Object.__init__(self)
        GEdit3TabSwitch.bool  = self.load()

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
        widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        button1 = Gtk.RadioButton(label="Press [_Tab/Shift+Tab] for switching through right/left tabs"
                                    , use_underline=True)
        button1.connect("toggled", self.on_checkbtn_toggled)
        button2 = Gtk.RadioButton(group=button1
        , label="Press [_PageUp/PageDown] for switching through right/left tabs", use_underline=True)
        if GEdit3TabSwitch.bool is True:
            button1.set_active(True)
            button2.set_active(False)
        elif GEdit3TabSwitch.bool is False:
            button2.set_active(True)
            button1.set_active(False)
        widget.set_border_width(6)
        title_label = Gtk.Label("Tab switching")
        Gtk.Widget.modify_font(title_label, Pango.font_description_from_string("14"))
        widget.add(title_label)
        widget.add(button1)
        widget.add(button2)
        return widget

    def on_checkbtn_toggled(self, checkbtn):
        GEdit3TabSwitch.bool = checkbtn.get_active()
        self.save(checkbtn.get_active())

    def load(self):
        """Loads language settings."""
        settings_path = self.get_path()
        if os.path.exists(settings_path):
            try:
                settings_file = open(settings_path, "rb")
                checkbtn = pickle.load(settings_file)
                settings_file.close()
                print("Loaded tab switching settings file successfully")
                return checkbtn
            except IOError:
                print("Failed to load settings.")
                return True
        else:
            return True

    def save(self, checkbtnvalue):
        """Saves language settings."""
        settings_path = self.get_path()
        try:
            settings_file = open(settings_path, "wb")
            pickle.dump(checkbtnvalue, settings_file)
            settings_file.close()
            print("Tab switching settings file saved successfully")
        except IOError:
            print("Failed to open the settings")
            label = Gtk.Label("Failed to open the settings")
            label.show()

    def get_path(self):
        """Returns the settings file path."""
        path = os.path.abspath(os.path.dirname (__file__))
        path += os.path.sep
        return path + self.SETTINGS_FILENAME

    def on_key_press_event(self, window, event):
        key = Gdk.keyval_name(event.keyval)
        #if tab
        if GEdit3TabSwitch.bool is True:
            shortcut = ('Tab', 'ISO_Left_Tab')
        elif GEdit3TabSwitch.bool is False:
            shortcut = ('Page_Down', 'Page_Up')
        if event.state & Gdk.ModifierType.CONTROL_MASK and key in shortcut:
            atab = window.get_active_tab()
            tabs = atab.get_parent().get_children()
            tlen = len(tabs)
            i = 0
            tab = atab
            #iterate through all tabs to get index
            for tab in tabs:
                i += 1
                if tab == atab:
                    break
            
            #if user wants to go to the left
            if key == 'ISO_Left_Tab' or key == 'Page_Up':
                i -= 2
            #if active tab is the first set active to the last
            if i < 0:
                tab = tabs[tlen-1]
            #if the active tab is the last one set active to the first
            elif i >= tlen:
                tab = tabs[0]
            else:
                tab = tabs[i]

            window.set_active_tab(tab)

            return True
