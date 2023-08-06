import ctypes
import inspect
import threading
import time


class Thread:
    def __init__(self, run, args=()):
        self.factory = threading.Thread(target=run, args=args, daemon=True)

    def is_alive(self):
        return self.factory.is_alive()

    def start(self):
        self.factory.start()

    def kill(self):
        tid = ctypes.c_long(self.factory.ident)
        exctype = SystemExit
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError('invalid thread id')
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError('PyThreadState_SetAsyncExc failed')

    def stop(self, sec=0.5):
        while self.is_alive():
            try:
                self.kill()
            except:
                pass
            finally:
                time.sleep(sec)
