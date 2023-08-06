# -*- coding: utf-8 -*- 
# Time: 2022-02-24 15:24
# Copyright (c) 2022
# author: Euraxluo

from redis import Redis
import pickle
import typing
import threading
import uuid


class Filed:

    def __init__(self, default, refresh=True):
        self.default = default  # value
        self.refresh = refresh  # dynamic refresh


class Meta(type):

    # getattr => return default
    def __setattr__(self, attr, value):
        # setattr =>  If the data is refresh, it is sent to the queue
        if self.__init_class__ and self.__enable__ and DynamicConfig.__config_data__[self.__key__][attr].refresh:
            with DynamicConfig.__redis__.pipeline(transaction=True) as pipe:
                pipe.publish(DynamicConfig.__channel__, pickle.dumps([DynamicConfig.__uuid__, self.__key__, attr, value], protocol=4))
                DynamicConfig.__config_data__[self.__key__][attr].default = value
                pipe.hset(self.__key__, attr, pickle.dumps(value, protocol=4))
                setattr_result = pipe.execute()
            if DynamicConfig.__logger__:
                DynamicConfig.__logger__.info(
                    f"subscribe message channel:{DynamicConfig.__channel__}, identify:{DynamicConfig.__uuid__},  sub_class:{self}, class_key:{self.__key__}, attr:{attr}, value:{value}, setattr_result:{setattr_result}")
        return super().__setattr__(attr, value)


class DynamicConfig(metaclass=Meta):
    __init_class__ = False
    __pubsub__ = False
    __enable__ = True
    __redis__: Redis = None
    __config_data__: typing.Mapping[str, typing.Mapping[str, Filed]] = {}
    __prefix__: str = "dynamic_config:"
    __key__: str = ""
    __channel__: str = "dynamic_config:channel"
    __uuid__: str = str(uuid.uuid1())
    __logger__ = None

    # 1. 继承该类的,解析获取每一个类的数据
    def __init_subclass__(cls, **kwargs):
        name = cls.__module__ + "." + cls.__name__
        property_dict = {}
        for k, v in cls.__dict__.items():
            if not k.startswith("__"):
                if isinstance(v, Filed):
                    super(Meta, cls).__setattr__(k, v.default)
                    property_dict[k] = v
                else:
                    property_dict[k] = Filed(v, refresh=False)

        # setting __prefix__ that is redis hash set key
        if cls.__prefix__ == DynamicConfig.__prefix__ or cls.__prefix__ == "":
            super(Meta, cls).__setattr__("__key__", DynamicConfig.__prefix__ + name)
        else:
            super(Meta, cls).__setattr__("__key__", DynamicConfig.__prefix__ + cls.__prefix__)

        if cls.__key__ in DynamicConfig.__config_data__:
            raise KeyError(f"cant use the same name as the __prefix__, cls:{cls},__prefix__:{cls.__prefix__},key:{cls.__key__}")
        DynamicConfig.__config_data__[cls.__key__] = property_dict

        # Refresh when subclasses load
        cls.refresh()
        cls.__init_class__ = True
        # A thread is started to wait for redis data to return
        if DynamicConfig.__enable__ and not DynamicConfig.__pubsub__:
            thread = threading.Thread(target=DynamicConfig.sub_data)
            thread.setDaemon(True)
            thread.start()
            DynamicConfig.__pubsub__ = True

    @classmethod
    def sub_data(cls: 'DynamicConfig'):
        pubsub = cls.__redis__.pubsub()
        pubsub.subscribe([cls.__channel__])
        for i in pubsub.listen():
            if i.get('type') == "message":
                message_data = i.get('data')
                identify, class_key, attr, value = pickle.loads(message_data)
                if identify != cls.__uuid__:
                    cls.__config_data__[class_key][attr].default = value
                    for sub_class in cls.__subclasses__():
                        if sub_class.__key__ == class_key and sub_class.__enable__:
                            if cls.__logger__:
                                cls.__logger__.info(f"subscribe message identify:{identify}, sub_class:{sub_class}, class_key:{class_key}, attr:{attr}, value:{value}")
                            super(Meta, sub_class).__setattr__(attr, value)
                            break

    @classmethod
    def register(cls: 'DynamicConfig', redis: Redis, enable: bool = True, logger=None):
        """
        Please register for Redis when first introducing DynamicConfig
        """
        cls.__redis__ = redis
        cls.__enable__ = enable
        cls.__logger__ = logger

    @classmethod
    def refresh(cls):
        if not DynamicConfig.__enable__:
            return

        cls.check_and_refresh_redis_property()

    @classmethod
    def check_and_refresh_redis_property(cls):
        if not DynamicConfig.__redis__:
            return
        with DynamicConfig.__redis__.pipeline(transaction=True) as pipe:
            for attr in DynamicConfig.__config_data__[cls.__key__]:
                pipe.hexists(cls.__key__, attr)
            exists_res = pipe.execute()
            for (attr, field), exists in zip(DynamicConfig.__config_data__[cls.__key__].items(), exists_res):
                if exists:
                    pipe.hget(cls.__key__, attr)
                else:
                    pipe.hset(cls.__key__, attr, pickle.dumps(field.default, protocol=4))
            getset_res = pipe.execute()

            for (attr, field), exists, getset in zip(DynamicConfig.__config_data__[cls.__key__].items(), exists_res, getset_res):
                if exists and field.refresh:
                    if getset is None:
                        value = getset
                    else:
                        value = pickle.loads(getset)
                    super(Meta, cls).__setattr__(attr, value)
                    field.default = value
