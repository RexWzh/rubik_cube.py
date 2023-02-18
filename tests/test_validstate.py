# test for validity of state

import unittest
from rubik.group import valid_centers, shift_color, init_state
# import kociemba as kb

class TestSimple(unittest.TestCase):

    def test_count():
        unittest.assertEqual(len(valid_centers), 12)
        unittest.assertEqual(len(set(valid_centers)), 12)

    def test_shift_color():
        for cens in valid_centers:
            state = shift_color(init_state, cens, skipcenter=True)
            # kb.solve(state)
        assert True


if __name__ == '__main__':
    unittest.main()