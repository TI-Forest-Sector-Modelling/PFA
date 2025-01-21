import unittest
from PNV.src import main
from PNV.src.logic import ProcessingArea


class TestPNVClass(unittest.TestCase):
    def test_main(self):
        """
        Unittest for the main function of the PFA project.
        """
        main.main(plot_fig=True)


if __name__ == '__main__':
    unittest.main()
    print("Finished")
