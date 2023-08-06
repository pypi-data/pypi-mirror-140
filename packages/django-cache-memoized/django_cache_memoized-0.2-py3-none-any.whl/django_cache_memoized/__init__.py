import re

from inspect import signature
from functools import wraps

from django.conf import settings
from django.core.cache import cache


class TooManyArgs(Exception):
    pass


class TooManyKwargs(Exception):
    pass


class TooFewArgs(Exception):
    pass


def memoized(function_or_key_pattern=None, method=False):
    '''
    A simple decorator which memoizes a function using the configured Django cache.

    That is the results of the function are cached against a key that is produced
    using a supplied or default pattern.

    There are three distinctways of sing this decorator:

    1. Without parentheses

        @memoized
        def my_function(arg ...)
            ...

        In which case the default key pattern will be used which is enough to
        uniquely identify the result (icluding the name of the funciton and module
        it bvelongs to and all of the arguments it was called with.

    2. With parentheses

        @memoized()
        def my_function(arg ...)
            ...

        Same result as 1.

    3. With arguments

        @memoized("my_function({arg},,,)")
        def my_function(arg ...)
            ...

        Now provides a pattern to use for the key. It is up to you of course to ensure it
        uniquely identifies a given result but it is as f-string that can refer to any of
        the arguments my_function supports (and should of course include some reference to
        them all if it is to uniquely identify a result.

    :param function_or_key_pattern: The function to be decorated or a key pattern depending on use case
    :param method: Force this to be considered a decorated method (inferred if first arg is 'self')

    Internal notes on Python decoration:

    When used without parentheses, then at time of decoration it is called with the to-be-decorated function
    as its first argument and no other arguments and Pythnon expects us to return a new function which will
    replace (take the name of) the to-be-deocrated function.

    When it is used with parentheses the it supports the two arguments above, neither mandatory and at the
    time of deocoration it is called with whatever arguments are provided (none if none ar provided) and
    Python expect us to return a function that it wil then call with the to-be-decorated function as its
    first and only argument.


    What this means is:

    When no parentheses are used, we return the decorated function - literally `decorate(function)`
    When parentheses are used, we return the function that decorates functions - literally just `decorate`

    functools.wraps ensures that `decorated` carreis all th emetadata of the function that is being deocrated
    (like __name__ and __doc__ etc.)

    `decorated` can see the arguments to memoized (they are in scope) and needs to interpret them.
    '''

    def decorate(fn):

        @wraps(fn)  # Preserves all of the metadata associated with fn
        def decorated(*args, **kwargs):
            # Interpret the arguments to memoized
            key_pattern = None if callable(function_or_key_pattern) else function_or_key_pattern
            is_method = method

            allargs = signature(fn).parameters

            # allargs is an OrderedDict, the keys of which are the arguments of fn.
            # We build therfrom, a list of arguments we are seeking in args and kwargs
            seeking = list(allargs.keys())
            found = {}

            # Methods by convention have the first argument "self". Even if it's
            # not a method, setting a local varials 'self' is fraught with issues
            # And so we need to remap it. Also if we've explicitly decorated a method
            # we remap the first argument. We call it 'selfie' interanally, but in provided
            # key_patterns, accept 'self' as a reference.
            if seeking[0] == 'self' or is_method:
                selfie = args[0]
                found['selfie'] = selfie
                seeking.pop(0)
                sarg = 1
                is_method = True
            else:
                sarg = 0

            # For classifying arguments see:
            # https://docs.python.org/3/library/inspect.html#inspect.Parameter
            #
            # We start by consuming all the args.
            if seeking:
                for arg in args[sarg:]:
                    # This should never happen, but if someone calls the decorated function
                    # with more args than the original function can accept that's clearly
                    # an erroneous call.
                    if len(seeking) == 0:
                        raise TooManyArgs(f"Decorated function has been called with {len(args)} positional arguments when only {len(allargs)} args are accepted by the decorated function. ")

                    # Set a local variable, feigning the conditions that fn would see
                    # if seeking[0] is 'self' this exhibits odd dysfunctional behaviour
                    # and so above we mapped 'self' to 'selfie' internall of this decorator.
                    found[seeking[0]] = arg
                    exec(f"{seeking[0]} = arg")
                    seeking.pop(0)

                # If we did not find all that we seek by consuming args, consume kwargs
                if seeking:
                    for kwarg, val in kwargs.items():
                        if kwarg in seeking:
                            # Should never happen, but if someone calls the decorated function
                            # with more args than the original function can accept that's clearly
                            # an erroneous call.
                            if len(seeking) == 0:
                                raise TooManyKwargs(f"Decorated function has been called with {len(kwargs)} keyword arguments after {len(args)} positional arguments when only {len(allargs)} args are accepted by the decorated function. ")

                            arg = seeking.index(kwarg)
                            found[seeking[arg]] = val
                            exec(f"{seeking[arg]} = val")
                            seeking.pop(arg)

                    if seeking:
                        # Any that remain we can check for default values
                        for arg in seeking:
                            props = allargs[arg]
                            if props.default != props.empty:
                                pos = seeking.index(arg)
                                found[seeking[pos]] = props.default
                                exec(f"{seeking[pos]} = props.default")
                                seeking.pop(pos)

                        # If any remain, then clearly not all the argument fn needs have been supplied
                        # to its decorated version.
                        if seeking:
                            raise TooFewArgs(f"Decorated function expects arguments ({', '.join(seeking)}), which it was not called with.")

            # Create a key for the Django cache
            # It should contain no spaces or unprintable chars.
            if not key_pattern is None:
                # If a pattern is supplied treat it as a f-string that references the arguments
                # (but permit the pattern to contain {self} and work with out internall reference (selfie)
                key_pattern = key_pattern.replace("{self}", "{selfie}")
                if 'selfie' in found: found['self'] = found['selfie']
                key = key_pattern.format(**found)
            elif is_method:
                # If the object is an instance of a Django model, it will have a primary ky ('pk' attribute)
                # if it not, but an instances of some other arbitrary class we can fall back on the objects 'repr'.
                klass = type(selfie).__name__
                pk = getattr(selfie, 'pk', None)
                if pk is None:
                    key = f"{repr(selfie)}.{fn.__name__}"
                else:
                    key = f"{klass}[{pk}].{fn.__name__}"
            else:
                # The default for ordinary functions will attempt a simple
                # repr like string that includes the module, function name and
                # it's arguments) hoping to unique describe a calling scenario.
                pfx = settings.CACHES[cache._alias].get('KEY_PREFIX', '')
                mod = re.sub(f"^{pfx}.", "", fn.__module__) if pfx else fn.__module__
                strargs = ','.join([f'{k}={v}' for k, v in found.items()])
                strargs = re.sub(f"^selfie=", "self=", strargs)
                key = f"{mod}.{fn.__name__}({strargs})"

            # Last safety measure to safeguard against spaces in the key:
            key = key.replace(" ", "_")

            # Finally do the actual memoizing
            value = cache.get(key)
            if value is None:
                # Call the deocrated function, and cache the result
                result = fn(*args, **kwargs)
                cache.set(key, result)
            else:
                # return the cached value
                result = value
            return result

        # Because this was decorated with functools.wraps(fn) it has all
        # the metadata of fn. Like .__name__ aand __doc__ etc.
        return decorated

    # If the first argument is a function and ther eis only one function then we assume
    # the deocrator was used without parentheses and return the decorated function.
    if callable(function_or_key_pattern) and method == False:
        return decorate(function_or_key_pattern)

    # Otherwise we return the function that will decorate (Pythin will then call it with
    # the to-be-decorated function
    else:
        return decorate

