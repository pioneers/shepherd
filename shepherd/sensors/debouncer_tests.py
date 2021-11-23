import unittest
import sys
sys.path.insert(1, '../')
from sensors_config import GenericButton
from debouncer import Debouncer
from utils import SHEPHERD_HEADER

class TestDebouncer(unittest.TestCase):

    def test_noise(self):
        linebreak_debounce_threshold = 10
        city_linebreak = GenericButton(name="city_linebreak", should_poll=True, identifier=0, ydl_header=SHEPHERD_HEADER.CITY_LINEBREAK, debounce_threshold=linebreak_debounce_threshold)
        d = Debouncer()
        for i in range(10):
            d.debounce(0, city_linebreak)
        for i in range(100):
            value = d.debounce(i % 2, city_linebreak)
            # 70% threshold should be exceeded in first 5 iterations
            if i < 5:
                self.assertEqual(value, 0)
            else:
                self.assertEqual(value, None)

if __name__ == '__main__':
    unittest.main()
