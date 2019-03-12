#!/bin/bash

export $(xargs -0 -a "/proc/$(pgrep gnome-session -n -U $UID)/environ")

export XDG_RUNTIME_DIR="/run/user/1000"

export $(egrep -z DBUS_SESSION_BUS_ADDRESS /proc/$(pgrep -u $LOGNAME gnome-session)/environ)

/usr/bin/darkice -c /home/livestream/darkice.cfg
