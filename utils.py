def convertSecondsToTime(duration_sec: int):
    minutes = duration_sec // 60
    remainder = duration_sec - (minutes * 60)
    return f"{minutes:02}:{remainder:02}"

def makeTimeStamp(position, range):
    positionHuman = convertSecondsToTime(position)
    rangeHuman = convertSecondsToTime(range)
    return f"{positionHuman} / {rangeHuman}"

import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        tic = time.perf_counter()
        value = func(*args, **kwargs)
        toc = time.perf_counter()
        elapsed_time = toc - tic
        print(f"Elapsed time: {elapsed_time:0.4f} seconds")
        return value
    return wrapper_timer