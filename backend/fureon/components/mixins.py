import threading


class SingletonMixin(object):
    __singleton_lock = None
    __singleton_instance = None

    @classmethod
    def instance(cls, *args, **kwargs):
        if not cls.__singleton_lock:
            cls.__singleton_lock = threading.Lock()

        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls(*args, **kwargs)
        return cls.__singleton_instance

