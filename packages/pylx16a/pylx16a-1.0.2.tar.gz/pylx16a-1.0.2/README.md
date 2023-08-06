# PyLX-16A

A modern Python library for controlling HiWonder's (previously LewanSoul's) LX-16A servos.

## Install and Setup

Simply copy `lx16a.py` into your project directory.

Don't try to guess the port your controller is connected to. On Linux, run `sudo dmesg` after plugging it in, which prints the most recent kernel messages. It should say something like `ch341-uart converter now attached to ttyUSB0`, in which case the port you want is `/dev/ttyUSB0`.

There's also the possibility that your program doesn't have access to the port you want to use. In this case, we need to modify the permissions of the port (e.g. `/dev/ttyUSB0`). To make it publicly readable and writable, run `sudo chmod a+rw /dev/ttyUSB0`.

## Documentation

Refer to `documentation.md`.

## Example program

```python
from math import sin, cos, pi
from lx16a import *
import time

LX16A.initialize("/dev/ttyUSB0")

try:
    servo1 = LX16A(1)
    servo2 = LX16A(2)
    servo1.set_angle_limits(0, 240)
    servo2.set_angle_limits(0, 240)
except ServoTimeoutError as e:
    print(f"Servo {e.id_} is not responding. Exiting...")
    quit()

t = 0
while True:
    servo1.move(sin(t) * 60 + 60)
    servo2.move(cos(t) * 60 + 60)

    time.sleep(0.05)
    t += 0.1
```
