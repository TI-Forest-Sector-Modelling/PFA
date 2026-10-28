import unittest
from PNV import main
from PNV.user_input.default_parameters import USER_INPUT, TOOLBOX_INPUT


class TestPNVClass(unittest.TestCase):
    def test_main(self):
        """
        Unittest for the main function of the PFA project.
        """
        main(pj_user_input=USER_INPUT, tb_user_input=TOOLBOX_INPUT)


if __name__ == '__main__':
    unittest.main()
    print("Finished")
