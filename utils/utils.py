from flask import request
import functools


def dev_mode(func):
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        debug = request.args.get('debug')
        if debug:
            # TODO: set some global debug flag, that will trigger naughty logs.
            # TODO: add noise
            print("Debug")
        return func(*args, **kwargs)
    return wrapper_debug

