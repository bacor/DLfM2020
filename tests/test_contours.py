import unittest
import numpy as np
from music21 import converter
from src.contours import interpolate_stream

class TestContourInterpolation(unittest.TestCase):

    def test_interpolate_stream(self):
        s = converter.parse('tinyNotation: C D E F')
        ys = interpolate_stream(s)
        self.assertEqual(type(ys), np.ndarray)
    
    def test_pitches(self):
        s = converter.parse('tinyNotation: C D E F')
        ys = interpolate_stream(s, num_samples=4)
        self.assertListEqual(list(ys), [48, 50, 52, 53])

    def test_durations(self):
        # Different note durations with a total duration of 12 16th notes
        s = converter.parse('tinyNotation: C4. D8 E16 F16 G8')
        target = [48, 48, 48, 48, 48, 48, 50, 50, 52, 53, 55, 55]
        ys = interpolate_stream(s, num_samples=12)
        self.assertListEqual(list(ys), target)

    def test_rests(self):
        s = converter.parse('tinyNotation: C4 r4 D4 r4 r4')
        #sound = [48, --, 50, --, --]
        target = [48, 48, 50, 50, 50]
        ys = interpolate_stream(s, num_samples=5)
        self.assertListEqual(list(ys), target)

    def test_phrase_starting_with_rest(self):
        s = converter.parse('tinyNotation: r4 C4 D8 r8')
        target = [48, 48, 50, 50]
        ys = interpolate_stream(s, num_samples=4)
        self.assertListEqual(list(ys), target)

    def test_num_samples(self):
        s = converter.parse('tinyNotation: C D E F')
        for N in range(10, 100, 10):
            ys = interpolate_stream(s, num_samples=N)
            self.assertEqual(len(ys), N)

if __name__ == '__main__':
    unittest.main()    