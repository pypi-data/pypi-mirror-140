from multiprocessing import Pool
import functools
import time
import time
import functools
import os
from colorama import init
from termcolor import colored

init()
_type_start_loading = colored('[Start Loading]', 'white', 'on_yellow')
_type_finished = colored('[Finished]', 'white', 'on_green')
_type_time_used = colored('[Time Used]', 'white', 'on_cyan')


def running_status(func):
    @functools.wraps(func)
    def print_exec_time(start_time, end='\n'):
        print(
            f"{_type_time_used} `{func.__name__}`, time: {round(time.time()-start_time,5)} sec", end=end)

    @functools.wraps(func)
    def wrap(*args, **kwargs):
        print(
            f"{_type_start_loading} `{func.__name__}` runnung with pid:", os.getpid())
        start_time = time.time()
        result = func(*args, **kwargs)
        print_exec_time(start_time)
        return result

    return wrap


class ParallelLoading():
    def __init__(self, locals, processes=4) -> None:
        self.pool = Pool(processes=processes)
        self.locals = locals
        self.results = []

    def add(self, save_to, target, args=(), kwargs={}):
        res = self.pool.apply_async(target, args=args, kwds=kwargs)
        self.results.append((save_to, res))

    @running_status
    def start_loading(self):
        for save_to, res in self.results:
            self.locals[save_to] = res.get()
            print(f"{_type_finished} `{save_to}`, save in local variables")
