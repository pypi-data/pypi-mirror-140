# DLApp
DLApp is the query utility for dictionary or list.

## Installation
```python
pip install dlapp
```

## Features
- support a simple wildcard characters ?, *, [], [!]
- support regex
- support custom keywords
- support SQL-like select statement
- support GUI application

## Dependencies
- [compare_version](https://pypi.org/project/compare_versions/)
- [pyyaml](https://pypi.org/project/PyYAML/)
- [python-dateutil](https://pypi.org/project/python-dateutil/)

## Usage
```bash
(vp37) C:\>dlapp --help
usage: dlapp [options]

dlapp application

optional arguments:
  -h, --help            show this help message and exit
  --gui                 launch a dlapp GUI application
  --filename FILENAME   a json, yaml, or csv file name
  --filetype {csv,json,yaml,yml}
                        a file type can be either json, yaml, yml, or csv
  --lookup LOOKUP       a lookup criteria for searching a list or dictionary
  --select SELECT_STATEMENT
                        a select statement to enhance multiple searching
                        criteria
  --tutorial            show dlapp tutorial
  --tutorial-csv        show csv tutorial
  --tutorial-json       show json tutorial
  --tutorial-yaml       show yaml tutorial

(vp37) C:\>
```

## Getting Started

### Development

```python
>>> # test data
>>> lst_of_dict = [
...     { "title": "ABC Widget", "name": "abc", "width": 500},
...     { "title": "DEF Widget", "name": "def", "width": 300},
...     { "title": "MNP Widget", "name": "mnp", "width": 455},
...     { "title": "XYZ Widget", "name": "xyz", "width": 600}
... ]
>>>
>>> from dlapp import DLQuery
>>>
>>> query_obj = DLQuery(lst_of_dict)
>>>
>>> # find any value of title starting with A or X
>>> query_obj.find(lookup="title=_wildcard([AX]*)")
['ABC Widget', 'XYZ Widget']
>>>
>>> # find any data of title starting with A or X 
>>> # and select title, width where width lt 550
>>> query_obj.find(lookup="title=_wildcard([AX]*)", select="SELECT title, width WHERE width lt 550")
[{'title': 'ABC Widget', 'width': 500}]
>>>
>>>
>>>
>>> # assuming /path/sample.json file has the same structure data as lst_of_dict
>>> from dlapp import create_from_json_file
>>>
>>> query_obj = create_from_json_file('/path/sample.json')
>>>
>>> query_obj.find(lookup="title=_wildcard([AX]*)")
['ABC Widget', 'XYZ Widget']
>>>
>>> # to query json string data, use
>>> from dlapp import create_from_json_data
>>>
>>>
>>>
>>> # to query yaml file, use
>>> from dlapp import create_from_yaml_file
>>>
>>> # to query yaml string data, use
>>> from dlapp import create_from_yaml_data
>>>
>>>
>>>
>>> # to query csv file, use
>>> from dlapp import create_from_csv_file
>>>
>>> # to query csv string data, use
>>> from dlapp import create_from_yaml_file
```

### Console command line

Open DLApp application
```bash
$ dl-app                      # using python entry point
$ dlapp --gui                 # using console command line
$ python -m dlapp --gui       # using python module invocation
```

Search json, yaml, or csv file
```bash
$ # assuming that /path/sample.json has the same structure data as lst_of_dict
$ dlapp --filename=/path/sample.json --lookup="title=_wildcard([AX]*)"
['ABC Widget', 'XYZ Widget']
$
$ dlapp --filename=/path/sample.json --lookup="title=_wildcard([AX]*)" --select="SELECT title, width WHERE width lt 550"
[{'title': 'ABC Widget', 'width': 500}]
$
$ # the same syntax can apply for yaml, yml, or csv file. 
```

## Bugs/Requests
Please use the [GitHub issue tracker](https://github.com/Geeks-Trident-LLC/dlapp/issues) to submit bugs or request features.

## Licenses
- [BSD 3-Clause License](https://github.com/Geeks-Trident-LLC/dlapp/blob/develop/LICENSE)

