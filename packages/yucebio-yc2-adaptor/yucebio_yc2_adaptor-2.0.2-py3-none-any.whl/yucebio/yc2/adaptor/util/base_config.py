# -*- coding: utf-8 -*-
from typing import Any
import os
import json5


DEFAULT_CONFIG_DIR = ".yucebioconfig"
DEFAULT_USER_CONFIG_DIR = 'config'

class Config(object):
    
    def __init__(self, name: str = None, path: str = None):
        """固定使用 ~/.yucebioconfig/{name}.json5

        Args:
            name (str, optional): 配置名称. Defaults to None.
            path (str, optional): 配置所在路径，若未指定，则固定使用~. Defaults to None.
        """
        self.configpath = self.detect_config_path(path or DEFAULT_CONFIG_DIR)
        self.name = name or DEFAULT_USER_CONFIG_DIR

        self.configfile = os.path.join(self.configpath, self.name + '.json5')
        self._config = self.load()

    def detect_config_path(self, path_name: str):
        path_in_cwd = os.path.join(os.curdir, path_name)
        if os.path.exists(path_in_cwd):
            return path_in_cwd
        return os.path.join(os.path.expanduser('~'), path_name)

    @property
    def config(self) -> dict:
        return self._config

    # 初始化
    def load(self):
        if not os.path.exists(self.configfile):
            return {}
        
        with open(self.configfile, encoding='utf8') as r:
            self._config: dict= json5.load(r)
        return self._config

    # 保存配置
    def save(self):
        if not os.path.exists(self.configpath):
            os.makedirs(self.configpath)
        with open(self.configfile, 'w') as w:
            json5.dump(self._config, w, indent=2)

    # 重新加载配置
    def reload(self):
        self.save()
        self._config = self.load()

    # 更新配置
    def update(self, data: dict):
        self._config.update(data)
        self.save()

    def clear(self, key: str=None, sep: str=None):
        """清除指定key对应的配置项，嵌套字段使用sep分隔。如 clear('a.b', sep='.')会清除字段a的子字段b的配置项

        Args:
            key (str, optional): 待清除的key. Defaults to None.
            sep (str, optional): 自定义嵌套字段分隔符. Defaults to None.
        """
        if not key:
            self._config = {}
        else:
            keys = [key] if not sep else key.split(sep)
            _ref, final_key = self._config, keys[-1]
            for k in keys[:-1]:
                if k not in _ref:
                    return
                _ref = _ref[k]
            
            if final_key in _ref:
                del _ref[final_key]
        self.save()

    def __getitem__(self, key: str, default=None) -> Any:
        return self.config.get(key, default)

    def __contains__(self, key: str) -> bool:
        return key in self.config

    def __setitem__(self, key: str, value: Any):
        self.config[key] = value

    def __call__(self, key: str, value: Any = None) -> Any:
        return self._config.get(key, value)

config = Config()
if __name__ == '__main__':
    print(config)