# ptb

![Usage](https://raw.githubusercontent.com/4thel00z/ptdb/master/ptdb.png)

## Motivation

pdb sucks, the other packages do weird stuff and type completion does not work in interact mode (looking at you ipdb).

## Installation

```
pip install ptb
```

## Usage

Simple do:

```python3
from ptdb import set_trace

# some where in your code do:

set_trace()

# Then just type the following to be thrown into a ptpython shell
interact
```


## License

This project is licensed under the GPL-3 license.
