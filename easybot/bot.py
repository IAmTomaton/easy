import time

import win32api
from threading import Thread


class Bot:

    def __init__(self, power_key):
        self._power_key = power_key
        self._listener = Listener()
        self._macros = []
        self._stop = True

    def start(self):
        self._stop = False
        thread = Thread(target=self._run)
        thread.start()

    def stop(self):
        self._stop = True

    def set_single_macro(self, key, func):
        self._listener.set_macro(Macro(key, func, single=True))

    def set_cyclical_macro(self, key, func):
        self._listener.set_macro(Macro(key, func))

    def set_cyclical_hold_macro(self, key, func):
        self._listener.set_hold_macro(Macro(key, func))

    def _run(self):
        down = False
        print('start bot')
        try:
            while not self._stop:
                if win32api.GetAsyncKeyState(self._power_key) < 0 and not down:
                    down = True
                    if not self._listener.work:
                        self._listener.start()
                    else:
                        self._listener.stop()
                if win32api.GetAsyncKeyState(self._power_key) >= 0:
                    down = False
                time.sleep(0.001)
        finally:
            self._listener.stop()
            print('stop bot')


class Listener:

    def __init__(self):
        self._stop = True
        self._macros = []
        self._hold_macros = []
        self._keys_down = {}

    def start(self):
        self._stop = False
        thread = Thread(target=self._run)
        thread.start()

    def stop(self):
        self._stop = True

    def set_macro(self, macro):
        self._macros.append(macro)

    def set_hold_macro(self, macro):
        self._hold_macros.append(macro)

    @property
    def work(self):
        return not self._stop

    def _run(self):
        print('start listener')
        try:
            while not self._stop:
                for macro in self._macros:
                    if win32api.GetAsyncKeyState(macro.key) < 0 and not self._keys_down[macro.key]:
                        self._keys_down[macro.key] = True
                        if not macro.work:
                            macro.start()
                        else:
                            macro.stop()
                    if win32api.GetAsyncKeyState(macro.key) >= 0:
                        self._keys_down[macro.key] = False
                for macro in self._hold_macros:
                    if win32api.GetAsyncKeyState(macro.key) < 0 and not self._keys_down[macro.key]:
                        self._keys_down[macro.key] = True
                        if not macro.work:
                            macro.start()
                    if win32api.GetAsyncKeyState(macro.key) >= 0:
                        self._keys_down[macro.key] = False
                        macro.stop()
                time.sleep(0.001)
        finally:
            for macro in self._macros:
                macro.stop()
            for macro in self._hold_macros:
                macro.stop()
            print('stop listener')


class Macro:

    def __init__(self, key, func, single=False):
        self.key = key
        self._stop = True
        self._func = func
        self._single = single
        self.t = 0

    @property
    def work(self):
        return not self._stop

    def start(self):
        self._stop = False
        thread = Thread(target=self._run)
        thread.start()

    def stop(self):
        self._stop = True

    def _run(self):
        print('start macro')
        if self._single:
            self._func()
            self._stop = True
        else:
            while not self._stop:
                self._func()
        print('stop macro')
