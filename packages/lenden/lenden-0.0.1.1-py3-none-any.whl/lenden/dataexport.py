from enum import Enum
import json


def compare(s, t):
    """Compare two list without check the index

    Args:
        s (list): List A
        t (list): List B

    Returns:
        [boolean]: True if the two list have the same values.
    """
    t = list(t)   # make a mutable copy
    try:
        for elem in s:
            t.remove(elem)
    except ValueError:
        return False
    return not t


class DisplayType(str, Enum):
    """Display Enum Type
    """
    grid = "grid"
    """Display Type grid.
    """
    row = "row"
    """Display Type row.
    """

class ResultType(str, Enum):
    """Result Enum Type
    """
    str = "str"
    """Result Type string.
    """
    int = "int"
    """Result Type integer.
    """
    float = "float"
    """Result Type float.
    """
    percent = "percent"
    """Result Type percent without the % simbol.
    """
    image = "image"
    """Result Type image.
    """
    images = "images"
    """Result Type array of images.
    """
    numberarray = "numberarray"
    """Result Type array number.
    """

class ResultSizeType(str, Enum):
    """Result Size Type.
    """
    normal = "normal"
    """Result Type normal.
    """
    wide = "wide"
    """Result Type wide.
    """
    big = "big"
    """Result Type big.
    """


class DataResults(object):
    def __init__(self, Description, Help, Type, Path, Size, Format):
        self.Description = Description
        self.Help = Help
        self.Type = Type
        self.Path = Path
        self.Size = Size
        self.Format = Format

    def __eq__(self, obj):
        return self.Description == obj.Description and self.Help == obj.Help \
            and self.Type == obj.Type and self.Path == obj.Path \
            and self.Size == obj.Size and self.Format == obj.Format

    def getJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    @classmethod
    def from_json(cls, data):
        return cls(**data)


class DataLog(object):
    def __init__(self, Description, Path):
        self.Description = Description
        self.Path = Path

    def __eq__(self, obj):
        r_local = self.Path
        r_obj = obj.Path
        return self.Description == obj.Description and compare(r_local, r_obj)

    def getJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    @classmethod
    def from_json(cls, data):
        return cls(**data)


class DataExport(object):
    def __init__(self, Version, HasError, DisplayType, Results,CleanPatterns=[], Logs=DataLog("", [])):
        """DataExport

        Args:
            Version ([float]): Number Version of the Model.
            HasError ([number]): 0  for Error and 1 for Not error
            DisplayType ([DisplayType]): Display Type
            Results ([list of DataResults]): List of DataResults
            CleanPatterns ([list of strings]):  pattern pathname files
            Logs (Message, List of path of logs files): Logs in case of errors . Defaults to DataLog("", []).
        """
        self.Version = Version
        self.HasError = HasError
        self.DisplayType = DisplayType
        if Results is None:
            Results = []
        self.Results = Results
        self.CleanPatterns = CleanPatterns
        if Logs is None:
            Logs = DataLog("", [])
        if Logs.Path is None:
            Logs.Path = []
        self.Logs = Logs

    def __eq__(self, obj):
        r_local = self.Results
        r_obj = obj.Results
        p_local = self.CleanPatterns
        p_obj = obj.CleanPatterns
        return self.Version == obj.Version and self.HasError == obj.HasError \
            and self.DisplayType == obj.DisplayType and compare(p_local,r_local) and compare(r_local, r_obj) and self.Logs == obj.Logs

    def getJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    @classmethod
    def from_json(cls, data):
        Logs = DataLog.from_json(data["Logs"])
        Results = list(map(DataResults.from_json, data["Results"]))
        return cls(data["Version"], data["HasError"], data["DisplayType"],Results,data["CleanPatterns"], Logs)
