### dynamic_config 
- name = "dynamic_config"
- description = "Distributed dynamic configuration based on Redis"
- authors = ["Euraxluo <euraxluo@qq.com>"]
- license = "The MIT LICENSE"
- repository = "https://github.com/Euraxluo/dynamic_config"

#### install
`pip install dynamic-config`

#### UseAge
```
from dynamic_config.dynamic_config import DynamicConfig, Filed
from example.conftest import rdb
from loguru import logger

DynamicConfig.register(rdb,logger=logger)

class ConfigTest(DynamicConfig):
    __prefix__ = "test_config"
    __enable__ = True
    x: str = None
    y: str = Filed(None)

print(ConfigTest.x)
print(ConfigTest.y)
ConfigTest.x = 10
ConfigTest.y = [1,2,3,4]
```