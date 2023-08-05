# sparrow_tool
[![image](https://img.shields.io/badge/Pypi-0.4.19-green.svg)](https://pypi.org/project/sparrow_tool)
[![image](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)
[![image](https://img.shields.io/badge/license-GNU_GPL--v3-blue.svg)](LICENSE)
[![image](https://img.shields.io/badge/author-kunyuan-orange.svg?style=flat-square&logo=appveyor)](https://github.com/beidongjiedeguang)


-------------------------
## Install
```bash
pip install sparrow-tool
pip install sparrow-tool[dev]

pip install -e .
pip install -e .[dev]
```


## Usage

### Safe logger in `multiprocessing`
```python
from sparrow.log import Logger
import numpy as np
logger = Logger(name='train-log', log_dir='./logs', )
logger.info("hello","numpy:",np.arange(10))

logger2 = Logger.get_logger('train-log')
print(id(logger2) == id(logger))
>>> True
```

