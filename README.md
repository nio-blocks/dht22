DHT22
=====
The DHT22 block will poll a [DHT22](http://dlnmh9ip6v2uc.cloudfront.net/datasheets/Sensors/Weather/RHT03.pdf) (also called AM2302 and RHT03), a digital relative humidty and temperature sensor using the [Adafruit DHT library](https://github.com/adafruit/Adafruit_Python_DHT) read_retry method. It is suggested not to poll the block at an interval less than 2 seconds.

This block is not currently compatible with the newest Raspberry Pi 3b+ release.

Properties
----------
- **pin_number**: Select which pin the DHT is connected on.

Inputs
------
- **default**: Any list of signals.

Outputs
-------
- **default**: Appends `temperature` and `humidity` values to the input signal.

Commands
--------
None

Dependencies
------------
None
