import unittest
from unittest.mock import patch
from src.lenden.dataexport import *
import json


class TestDataResults(unittest.TestCase):

    def get_DataResults1(self):
        desc = "Irure aute ex irure fugiat."
        help = "Ex consequat nostrud enim nulla dolore incididunt officia ullamco ut consequat mollit nulla."
        type = ResultType.image
        path = "/path/to/image"
        size = ResultSizeType.normal
        format = "f2%"
        dataR1 = DataResults(Description=desc, Help=help,
                             Type=type, Path=path, Size=size, Format=format)
        return dataR1

    def get_DataResults2(self):
        desc = "Dolore culpa duis duis nulla duis eiusmod ullamco adipisicing aliqua."
        help = "Dolore mollit nulla.Nulla amet quis ad deserunt sit laboris irure incididunt est ea occaecat sunt."
        type = ResultType.numberarray
        path = "/path/to/numbersfile"
        size = ResultSizeType.big
        format = "%f12%"
        data1 = DataResults(Description=desc, Help=help,
                            Type=type, Path=path, Size=size, Format=format)
        return data1

    def test_Create_Constructor_DataResults(self):
        desc = "Irure aute ex irure fugiat."
        help = "Ex consequat nostrud enim nulla dolore incididunt officia ullamco ut consequat mollit nulla."
        type = ResultType.image
        path = "/path/to/image"
        size = ResultSizeType.normal
        format = "f2%"
        data = self.get_DataResults1()

        self.assertEqual(desc, data.Description)
        self.assertEqual(help, data.Help)
        self.assertEqual(type, data.Type)
        self.assertEqual(path, data.Path)
        self.assertEqual(size, data.Size)
        self.assertEqual(format, data.Format)

    def test_DataResults_Not_Equals(self):
        data1 = self.get_DataResults1()
        data2 = self.get_DataResults2()
        self.assertNotEqual(data1, data2)

    def test_DataResults_GetJSON(self):
        data1 = self.get_DataResults1()
        dataR1json = data1.getJSON()
        self.assertTrue(len(dataR1json) > 0)
        self.assertTrue(dataR1json.index(data1.Description) > 0)

    def test_DataResults_LoadJSON(self):
        """Test Load DataResults from JSON
        """
        desc = "Irure aute ex irure fugiat."
        help = "Ex consequat nostrud enim nulla dolore incididunt officia ullamco ut consequat mollit nulla."
        type = ResultType.image
        path = "/path/to/image"
        size = ResultSizeType.normal
        format = "f2%"
        datajson = '{"Description": "Irure aute ex irure fugiat.", "Help": "Ex consequat nostrud enim nulla dolore incididunt officia ullamco ut consequat mollit nulla.", "Type": "image", "Path": "/path/to/image", "Size": "normal", "Format": "f2%"}'
        data = DataResults.from_json(json.loads(datajson))
        self.assertEqual(desc, data.Description)
        self.assertEqual(help, data.Help)
        self.assertEqual(type, data.Type)
        self.assertEqual(path, data.Path)
        self.assertEqual(size, data.Size)
        self.assertEqual(format, data.Format)
