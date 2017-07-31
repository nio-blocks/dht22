from enum import Enum
import os
import subprocess
import re
import tempfile
from threading import Thread

from nio.block.base import Block
from nio.signal.base import Signal
from nio.properties.select import SelectProperty
from nio.properties.list import ListProperty
from nio.properties.string import StringProperty
from nio.properties.int import IntProperty
from nio.properties.string import StringProperty
from nio.properties.bool import BoolProperty
from nio.properties.timedelta import TimeDeltaProperty
from nio.properties.holder import PropertyHolder
from nio.util.discovery import discoverable

code_dir = os.path.dirname(os.path.realpath(__file__))
dht_path = os.path.join(code_dir, 'dht_bash')


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


@discoverable
class DHT22(Block):

    """ A block enriches incoming signals with the current values of a
    set of input pins.

    """
    pin_number = IntProperty(title='Pin Number', default=0)

    def process_signals(self, signals):
        for signal in signals:
            self._read_pin(signal)
        self.notify_signals(signals)

    def _read_pin(self, signal):
        try:
            for _ in range(3):
                command = Command(
                    [dht_path, "2302", str(self.pin_number())], timeout=2)
                output = command.run()
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
