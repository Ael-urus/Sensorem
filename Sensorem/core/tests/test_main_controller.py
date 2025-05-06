# core/tests/test_main_controller.py
import unittest
import os
from core.controllers.main_controller import MainController
from core.models.data_model import DataModel

class TestMainController(unittest.TestCase):
    def setUp(self):
        self.model = DataModel()
        self.controller = MainController(self.model)

    def test_load_csv(self):
        temp_file = os.path.join(str(self.controller.base_dir), "test.csv")
        with open(temp_file, "w") as f:
            f.write("time,value\n0,1.0\n1,2.0")
        self.controller.load_csv("test.csv")
        self.assertIsNotNone(self.model.csv_data)
        self.assertEqual(len(self.model.csv_data), 2)
        os.remove(temp_file)

if __name__ == "__main__":
    unittest.main()