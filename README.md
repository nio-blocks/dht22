DHT22
=====
For use with the [DHT22](http://dlnmh9ip6v2uc.cloudfront.net/datasheets/Sensors/Weather/RHT03.pdf) (also called AM2302), a digital relative humidty and temperature sensor.

dht_bash is from the [Adafruit library](https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_DHT_Driver/Adafruit_DHT)

Properties
----------

-   **pins**: Select which pins the DHT is connected on
 -   **name**: The name of the pin. All pins are put through a pin.name.format(pin.number)
 -   **number**: The pin number

Dependencies
------------
-   linsensors

Commands
--------
None

Input
-----
Any signal

Output
------
The pin names are appended onto the input signal with their value

