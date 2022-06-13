import dbus
from gi.repository import GLib
bus = dbus.SystemBus()

player = bus.get_object('org.bluez','/org/bluez/hci0/dev_F8_87_F1_B6_49_1B/player0')
BT_Media_iface = dbus.Interface(player, dbus_interface='org.bluez.MediaPlayer1')
BT_Media_props = dbus.Interface(player, "org.freedesktop.DBus.Properties")
print(BT_Media_props, dir(BT_Media_props))
props = BT_Media_props.GetAll("org.bluez.MediaPlayer1")
print(props)