import unittest
from src.lenden.dataexport import *


class TestDataExports(unittest.TestCase):

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

    def test_DataExport_Not_Equals(self):
        data1 = self.get_DataResults1()
        data2 = self.get_DataResults2()

        data = DataExport(Version=0.1, HasError=False,
                          DisplayType=DisplayType.grid, Results=[data1, data2], Logs=None)

        dem0 = data.getJSON()
        #print(dem0)
        data2 = DataExport.from_json(json.loads(dem0))

        self.assertEqual(data, data2)

    def test_DataExport_With_Error(self):
        data = DataExport(Version=0.1, HasError=True,
                          DisplayType=DisplayType.grid, Results=[],
                          Logs=DataLog("Voluptate sint sint eu aliqua consequat culpa nisi fugiat nostrud aute adipisicing.", ["/path/log1", "/path/log2", "/path/log3"]))

        dem0 = data.getJSON()
        #print(dem0)
        data2 = DataExport.from_json(json.loads(dem0))

        self.assertEqual(data, data2)
