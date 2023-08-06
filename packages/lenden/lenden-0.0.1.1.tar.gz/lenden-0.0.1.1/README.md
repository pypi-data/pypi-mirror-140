# lenden

Exchange Workflow Data

- 📙 *lenden for  exchange*

This library allows to express in a Json format the  output of the a [Radiomics](https://radiomicsgroup.github.io/) pipeline.

## Installation

To install execute the command

```bash
pip install lenden
```

## Use examples

An example pipeline with two outputs results.

```python
from lenden.dataexport  import *

result1= DataResults(Description="Do exercitation occaecat Lorem dolore labore culpa quis.", 
                     Help="Aliquip commodo sunt adipisicing officia irure laborum reprehenderit nulla consectetur in minim.",
                     Type=ResultType.image, Path="/path/to/image", Size=ResultSizeType.normal, Format="%20f")

result2= DataResults(Description="Sit pariatur magna nisi do.", 
                     Help="Velit id adipisicing tempor Lorem. Tempor dolore proident ea quis.",
                     Type=ResultType.percent, Path="/path/to/fileresult", Size=ResultSizeType.wide, Format="RGB(2,3,4)")
# Result without Error
data = DataExport(Version=0.1, HasError=False,
                          DisplayType=DisplayType.grid, Results=[result1, result2],CleanPatterns=['*.tmp'], Logs=None)
print(data.getJSON())
```

Then the output is:

```json
{
    "Version": 0.1,
    "HasError": false,
    "DisplayType": "grid",
    "Results": [
        {
            "Description": "Do exercitation occaecat Lorem dolore labore culpa quis.",
            "Help": "Aliquip commodo sunt adipisicing officia irure laborum reprehenderit nulla consectetur in minim.",
            "Type": "image",
            "Path": "/path/to/image",
            "Size": "normal",
            "Format": "%20f"
        },
        {
            "Description": "Sit pariatur magna nisi do.",
            "Help": "Velit id adipisicing tempor Lorem. Tempor dolore proident ea quis.",
            "Type": "percent",
            "Path": "/path/to/fileresult",
            "Size": "wide",
            "Format": "RGB(2,3,4)"
        }
    ],
    "CleanPatterns":["*.tmp"],
    "Logs": {
        "Description": "",
        "Path": []
    }
}
```

If exist an error then

```python

# Result with error
dataWithError = DataExport(Version=0.1, HasError=True,
                          DisplayType=DisplayType.grid, Results=[],CleanPatterns=['*.tmp'],
                          Logs=DataLog("Voluptate sint sint eu aliqua consequat culpa nisi fugiat nostrud aute adipisicing.", 
                                       ["/path/log1","/path/log2","/path/log3"]))
print(dataWithError.getJSON())
```

Then the output is:

```json
{
    "Version": 0.1,
    "HasError": true,
    "DisplayType": "grid",
    "Results": [],
    "CleanPatterns":["*.tmp"],
    "Logs": {
        "Description": "Voluptate sint sint eu aliqua consequat culpa nisi fugiat nostrud aute adipisicing.",
        "Path": [
            "/path/log1",
            "/path/log2",
            "/path/log3"
        ]
    }
}
```
