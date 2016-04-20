import time
from nio.block.terminals import DEFAULT_TERMINAL
from nio.testing.block_test_case import NIOBlockTestCase
from nio.signal.base import Signal
from ..dht_block import DHT

class TestDHTBlock(NIOBlockTestCase):

    def test_dht_read(self):
        notified = 0
        dht = DHT()
        self.configure_block(dht, {})
        dht.start()
        # just read some temperatures and print them
        for _ in range(5):
            dht.process_signals([Signal({"value": "test"})])
            notified += 1
            self.assert_num_signals_notified(notified, dht)
            self.assertTrue('temperature' in \
                            self.last_notified[DEFAULT_TERMINAL][0].to_dict())
            self.assertTrue('humidity' in \
                            self.last_notified[DEFAULT_TERMINAL][0].to_dict())
            time.sleep(3)
        dht.stop()
