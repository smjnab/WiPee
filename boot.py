# Turn off network ASAP. If wipy has to publish MQTT message, it will enable the wifi.
from network import WLAN

wlan = WLAN(mode=WLAN.STA)
wlan.disconnect()
