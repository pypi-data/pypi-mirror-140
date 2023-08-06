# https://pypi.org/project/kthread/

# Modules
import ctypes
import inspect
import threading

# Exception raiser
def _async_raise(tid, exctype) -> None:
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")

    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("Invalid thread ID")

    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")

# Killable thread
class KThread(threading.Thread):
    def _get_my_tid(self) -> int:
        if not self.is_alive():
            raise threading.ThreadError("Thread is not active")

        if hasattr(self, "_thread_id"):
            return self._thread_id

        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid

        raise AssertionError("Could not determine the thread's ID")

    def raise_exc(self, exctype: Exception) -> None:
        _async_raise(self._get_my_tid(), exctype)

    def terminate(self) -> None:
        self.raise_exc(SystemExit)
