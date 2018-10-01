from nio import Block, Signal
from nio.properties import VersionProperty, IntProperty

import Adafruit_DHT as DHT


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
            temp, hum = DHT.read_retry(DHT.DHT22, self.pin_number())
            self.logger.debug("Temp, Hum = {}".format(temp, hum))
            temp = float(temp)
            hum = float(hum)
            setattr(signal, 'temperature', temp)
            setattr(signal, 'humidity', hum)
        except:
            self.logger.exception("Error reading pin")
