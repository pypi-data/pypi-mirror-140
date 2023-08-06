from functools import wraps
from threading import Thread, Lock
from typing import Callable

# 单例模式
class Singleton(type):
    _instance_lock = Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with Singleton._instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


'''
#元类
class SingClass(metaclass=Singleton):
    def __init__(self):
        pass
'''

class SingleInstance(object):
    _instance_lock = Lock()
    _instance = None

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(SingleInstance, '_instance'):
            with SingleInstance._instance_lock:
                if not hasattr(SingleInstance, '_instance'):
                    SingleInstance._instance = SingleInstance(*args, **kwargs)
        return SingleInstance._instance


def daemon_thread(fn: Callable) -> Callable[..., Thread]:

    @wraps(fn)
    def _wrap(*args, **kwargs) -> Thread:
        return Thread(target=fn, args=args, kwargs=kwargs, daemon=True)

    return _wrap

'''
 @daemon_thread
    def thread_func():
        pass
'''