from typing import *
class iniEnum:
    m: int
    @property
    def r(self) -> int:
        return 0
    @property
    def w(self) -> int:
        return 1
    @property
    def rw(self) -> int:
        return -1
    @property
    def mode(self) -> int:
        return self.m
    def __init__(self, mode: int):
        setattr(self, 'm', mode)
iniFile = None
class iniObject:
    @property
    def name(self):
        return self.key
    def __init__(self,config: dict[str,str], mode: iniEnum, cls: ClassVar, key: Any=None) -> None:
        self.config = config
        self.mode = mode.mode
        self.cls = cls
        self.key = key
    @property
    def readable(self) -> bool:
        return self.mode == iniEnum.r or self.mode == iniEnum.rw
    @property
    def writable(self) -> bool:
        return self.mode == iniEnum.w or self.mode == iniEnum.rw
    if readable:
        def __getitem__(self, item) -> str:
            return self.config[item]
        def get(self, key, default=None) -> str:
            return self.config.get(key, default)
    if writable:
        def __setitem__(self, key, value) -> None:
            self.config[key] = value
        def pop(self, key, default=None) -> str:
            return self.config.pop(key, default)
        def clear(self) -> None:
            self.config.clear()
        if name is not None:
            def apply(self) -> None:
                self.cls[self.key] = self.config
    def items(self):
        return self.config.items()
    def keys(self):
        return self.config.keys()
    def values(self):
        return self.config.values()
class ini:
    config: dict[str, dict[str, str]] = {}
    mode: int
    file: IO
    def __init__(self, file: IO):
        mode = iniEnum.r
        if file.readable() and file.writable():
            mode = iniEnum.rw
        elif file.readable():
            mode = iniEnum.r
        elif file.writable():
            mode = iniEnum.w
        setattr(self, "mode", mode)
        setattr(self, "file", file)
        if mode == iniEnum.r or mode == iniEnum.rw:
            f = file.readlines()
            cfgName = ''
            gets = {}
            i = ""
            for i in f:
                i = i.replace('\n','')
                if i.startswith('[') and i.endswith(']'):
                    if cfgName != '':
                        self.config[cfgName] = gets
                        gets = {}
                    cfgName = i.replace('[', '').replace(']', '')
                else:
                    if '=' in i:
                        splits = i.split('=')
                        key = splits[0]
                        value = "".join(splits[1:])
                        gets[key] = value
                    else:
                        continue
            if i != "":
                self.config[cfgName] = gets
            del cfgName
            del gets

    @property
    def readable(self) -> bool:
        return self.mode == iniEnum.r
    @property
    def writable(self) -> bool:
        return self.mode == iniEnum.w
    if writable:
        def __setitem__(self, key, value) -> None:
            self.config[key] = value
        def createObject(self, key, values: dict[str,str]=None) -> iniObject:
            o = iniObject(config=values if values is not None else {}, mode=iniEnum(mode=self.mode), cls=self, key=key)
            return o
        def pop(self, key, default=None) -> iniObject:
            return iniObject(config=self.config.pop(key, default), mode=iniEnum(mode=self.mode), cls=self, key=None)
        def clear(self) -> None:
            self.config.clear()
        def write(self) -> None:
            text = ""
            for i in self.config:
                text += f"[{i}]\n"
                for t in self.config[i]:
                    text += f"{t}={self.config[i][t]}\n"
            self.file.write(text)
    if readable:
        def __getitem__(self, item) -> iniObject:
            return iniObject(config=self.config[item], mode=iniEnum(mode=self.mode), cls=self, key=item)
        def get(self, key, default=None) -> iniObject:
            return iniObject(config=self.config.get(key, default), mode=iniEnum(mode=self.mode), cls=self, key=key)
iniFile = ini