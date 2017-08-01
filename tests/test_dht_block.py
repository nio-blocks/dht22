from unittest.mock import patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.testing.block_test_case import NIOBlockTestCase
from nio.signal.base import Signal
from ..dht_block import DHT22


class TestDHTBlock(NIOBlockTestCase):

    def test_dht_read(self):
        notified = 0
        dht = DHT22()
        self.configure_block(dht, {})
        dht.start()
        for i in range(5):
            with patch(DHT22.__module__ + ".Command.run") as mock_run:
                mock_run.return_value = "Temp = 1.23 Hum = 4.56"
                dht.process_signals([Signal({"value": "test"})])
            self.assert_num_signals_notified(i+1, dht)
            last_signal = self.last_notified[DEFAULT_TERMINAL][-1].to_dict()
            self.assertDictEqual(last_signal, {
                "value": "test",
                "temperature": 1.23,
                "humidity": 4.56,
            })
        dht.stop()
