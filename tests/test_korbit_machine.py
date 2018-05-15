import unittest
from autotrading.machine.korbit_machine import KorbitMachine
import inspect

class KorbitMachineTestCase(unittest.TestCase):

    def setUp(self):
        self.korbit_machine = KorbitMachine()
#        self.korbit_machine.set_token()

    def tearDown(self):
        pass
