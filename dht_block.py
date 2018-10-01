import re

from nio import Block, Signal
from nio.properties import VersionProperty, IntProperty

import Adafruit_DHT


class DHT22(Block):

    """ A block enriches incoming signals with the current values of a
    set of input pins.

    """
    pin_number = IntProperty(title='Pin Number', default=0)
    version = VersionProperty("1.0.0")

    def process_signals(self, signals):
        for signal in signals:
            self._read_pin(signal)
        self.notify_signals(signals)

    def _read_pin(self, signal):
        try:
            for _ in range(3):
                output = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, self.pin_number())
                temp = re.search("Temp =\s+([0-9.]+)", output)
                hum = re.search("Hum =\s+([0-9.]+)", output)
                self.logger.debug("Temp, Hum = {}".format(temp, hum))
                if not temp or not hum:
                    self.logger.debug("Retrying DHT")
                    continue
                temp = float(temp.group(1))
                hum = float(hum.group(1))
                setattr(signal, 'temperature', temp)
                setattr(signal, 'humidity', hum)
                break
            else:
                raise IOError("Cannot read from device")
        except:
            self.logger.exception("Error reading pin")
