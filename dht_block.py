from enum import Enum
import os
import subprocess
import re
import tempfile

from nio.common.block.base import Block
from nio.common.signal.base import Signal
from nio.metadata.properties.select import SelectProperty
from nio.metadata.properties.list import ListProperty
from nio.metadata.properties.string import StringProperty
from nio.metadata.properties.int import IntProperty
from nio.metadata.properties.string import StringProperty
from nio.metadata.properties.bool import BoolProperty
from nio.metadata.properties.timedelta import TimeDeltaProperty
from nio.metadata.properties.holder import PropertyHolder
from nio.common.discovery import Discoverable, DiscoverableType
from nio.modules.threading import Thread

from linsensors.htu21d import Htu21d

code_dir = os.path.dirname(os.path.realpath(__file__))
dht_path = os.path.join(code_dir, 'dht_bash')

class DeviceType(Enum):
    DHT22 = 'DHT22'
    HTU21DF = 'HTU21D-F'

htu_addresses = {0: 0x0703}

class Command:
    def __init__(self, cmd, timeout=1):
        self.cmd = cmd
        self.timeout = timeout
        self.process = None
        self.output = None

    def run(self):
        self.process = None
        self.output = None
        thread = Thread(target=self._target)
        thread.start()
        thread.join(self.timeout)
        if thread.is_alive():
            self.process.terminate()
            self.process = None
            thread.join()
            raise TimeoutError(self.timeout)
        out = self.output.decode()
        self.process = None
        self.output = None
        return out

    def _target(self):
        with tempfile.SpooledTemporaryFile() as pipe:
            self.process = subprocess.Popen(self.cmd, stdout=pipe)
            self.process.communicate()
            pipe.flush()
            pipe.seek(0)
            self.output = pipe.read()


class Pin(PropertyHolder):
    name = StringProperty(title="Name", default="pin{}_value")
    number = IntProperty(title='Number', default=0)
    device = SelectProperty(DeviceType, default=DeviceType.HTU21DF, title="DHT sensor")


@Discoverable(DiscoverableType.block)
class DHT(Block):

    """ A block enriches incoming signals with the current values of a
    set of input pins.

    """
    pins = ListProperty(Pin, title='Devices')

    def configure(self, context):
        super().configure(context)
        self.dht22 = [s for s in self.pins if s.device is DeviceType.DHT22]
        htu = (s for s in self.pins if s.device is DeviceType.HTU21DF)
        self.htu = [(h.name.format(h.number), Htu21d(htu_addresses[h.number])) for h in htu]

    def process_signals(self, signals):
        values = {}
        values.update(self._read_htus())
        for s in signals:
            self._read_pins(s)
            for key, value in values.items():
                setattr(s, key, value)

        self.notify_signals(signals)

    def _read_htus(self):
        values = {}
        for name, h in self.htu:
            try:
                values[name] = {'temperature': h.read_temperature(), 'humidity': h.read_humidity()}
            except Exception as e:
                self._logger.error(
                    "Error reading device {}: {} {}".format(
                        name, type(e), str(e)
                    )
                )
        return values


    def _read_pins(self, signal):
        for pin in self.dht22:
            attr = pin.name.format(pin.number)
            try:
                for _ in range(3):
                    command = Command([dht_path, "2302", str(pin.number)], timeout = 2)
                    output = command.run()
                    temp = re.search("Temp =\s+([0-9.]+)", output)
                    hum = re.search("Hum =\s+([0-9.]+)", output)
                    self._logger.debug("Temp, Hum = {}".format(temp, hum))
                    if not temp or not hum:
                        self._logger.debug("Retrying DHT")
                        continue
                    temp = float(temp.group(1))
                    hum = float(hum.group(1))
                    setattr(signal, attr, {'temperature': temp, 'humidity': hum})
                    break
                else:
                    raise IOError("Cannot read from device")
            except Exception as e:
                self._logger.warning(
                    "Error reading pin {}: {}".format(
                        type(e), str(e)
                    )
                )
