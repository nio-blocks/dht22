from unittest.mock import patch, MagicMock
from nio.block.terminals import DEFAULT_TERMINAL
from nio.testing.block_test_case import NIOBlockTestCase
from nio import Signal
import sys


class TestDHTBlock(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        sys.modules['Adafruit_DHT'] = MagicMock()
        from ..dht_block import DHT22
        global DHT22

    def test_dht_read(self):
        notified = 0
        dht = DHT22()
        self.configure_block(dht, {})
        dht.start()
        for i in range(5):
            with patch(DHT22.__module__ + ".DHT.read_retry") as mock_read:
                mock_read.return_value = ("1.23", "4.56")
                dht.process_signals([Signal({"value": "test"})])
            self.assert_num_signals_notified(i+1, dht)
            last_signal = self.last_notified[DEFAULT_TERMINAL][-1].to_dict()
            self.assertDictEqual(last_signal, {
                "value": "test",
                "temperature": 1.23,
                "humidity": 4.56,
            })
        dht.stop()
