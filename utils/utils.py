from flask import request
import functools
import logging


def debug(_func=None, *, _debug=False, _args_kwargs=True, _returned_value=True, logger=logging.getLogger()):
    def decorator_debug(func):
        @functools.wraps(func)
        def wrapper_debug(*args, **kwargs):
            _debug = request.args.get('debug')
            if _debug == 'True':
                signature = ''
                if _args_kwargs:
                    args_repr = [repr(a) for a in args]
                    kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                    signature = ", ".join(args_repr + kwargs_repr)
                    logger.setLevel(logging.DEBUG)
                    logger.debug(f"Calling {func.__name__}({signature})")
                else:
                    logger.debug(f'Calling {func.__name__}')

            value = func(*args, **kwargs)

            if _debug == 'True':
                if _returned_value:
                    logger.debug(f"{func.__name__!r} returned {value!r}")
            return value

        return wrapper_debug

    if _func is None:
        return decorator_debug
    else:
        return decorator_debug(_func)


def add_to_invoice(service, price):
    logging.info(f"Used Service: {service}. Invoice Total: {price}")


def parse_log(log):
    pass


def string_to_bool(text):
    if text in ('True', 'true', 'yes', 'Yes'):
        return True
    elif text in ('False', 'false', 'no', 'No'):
        return False
    elif text:
        return text
