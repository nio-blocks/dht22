import time

from nio.modules.threading import sleep
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.modules.scheduler import SchedulerModule
from nio.common.signal.base import Signal

from ..dht_block import DHT

def make_signals(num=1):
    return [Signal({"value": "test"}) for _ in range(num)]

class TestDHTBlock(NIOBlockTestCase):
    def signals_notified(self, signals):
        self._signals = signals

    def test_dht_read(self):
        notified = 0

        dht = DHT()
        self.configure_block(dht, {
            "pins": [
                {"name": "pin_value",
                 "number": 0}]
            })
        dht.start()
        # just read some temperatures and print them
        print("#### Printing some DHT data")
        for _ in range(5):
            dht.process_signals(make_signals())
            notified += 1
            self.assert_num_signals_notified(notified, dht)
            print(self._signals[0].pin_value)
            time.sleep(3)

        dht.stop()
