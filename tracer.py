import sys
import os
import time
import traceback
import functools
import platform
import inspect

# TODO1 maybe its own repo? No dependencies on sublime, pure python.
#   Integrate with simple logger too? With rdb?


# TODO1 doc:
# T(a, b, c, ...) printable things
# 0000.110 a_test_class.__init__:10 [making one a_test_class] [5] 
# sec.usec func-or-class.func:line-num [arg1] [arg2]...
# 
# function decorator yields:
# 0000.146 test_class_do_something:enter [<SbotDev.trace_test.a_test_class object at 0x000001B550FA7CD0>] [5] 
# sec.usec func-or-class.func:enter [arg1] [arg2]...
# 
# 0000.159 test_class_do_something:exit [5-glom-5] 
# sec.usec func-or-class.func:exit [result]

# TODO1 add:
# maybe A(func(xxx)) => sec.usec func:line-num [arg1] [result]
# assert: A(condition) if false raise something
# enable/disable T()/A(). production skips everything

# optional marker like >>>?

#-----------------------------------------------------------------------------------
#---------------------------- Private fields ---------------------------------------
#-----------------------------------------------------------------------------------

# The trace file.
_ftrace = None

# For elapsed time stamps.
_trace_start_time = 0


#-----------------------------------------------------------------------------------
#---------------------------- Public trace functions -------------------------------
#-----------------------------------------------------------------------------------

#---------------------------------------------------------------------------
def start_trace(trace_fn, clean_file=True):
    '''Enables tracing and optionally clean file (default is True).'''
    global _ftrace
    global _trace_start_time

    stop_trace()  # just in case

    if clean_file:
        with open(trace_fn, 'w'):
            pass

    # Open file now. Doing it on every write is too expensive.
    _ftrace = open(trace_fn, 'a')
    _trace_start_time = _get_ns()


#---------------------------------------------------------------------------
def stop_trace(): #TODO1 make sure this always gets called!
    '''Stop tracing.'''
    global _ftrace

    if _ftrace is not None:
        _ftrace.flush()
        _ftrace.close()
        _ftrace = None


#---------------------------------------------------------------------------
def T(*msgs):
    '''Trace function for user code.'''
    if _ftrace is not None:
        # Dig out func and line.
        frame = sys._getframe(1)
        if 'self' in frame.f_locals:
            class_name = frame.f_locals['self'].__class__.__name__
            func = f'{class_name}.{frame.f_code.co_name}'
        else:
            func = frame.f_code.co_name  # could be '<module>'

        msgl = []
        for m in msgs:
            msgl.append(m)

        _trace(func, frame.f_lineno, msgl)


#---------------------------------------------------------------------------
def traced_function(f):
    '''Decorator to support function entry/exit tracing.'''

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        res = None

        # Check for enabled.
        if _ftrace is not None:
            # Instrumented execution.
            msgs = []
            if len(args) > 0:
                for i in range(len(args)):
                    msgs.append(f'{args[i]}') # nice to have name but difficult
            if len(kwargs) > 0:
                for k,v in kwargs.items():
                    msgs.append(f'{k}:{v}')

            _trace(f.__name__, 'enter', msgs)

            # Execute the wrapped function.
            ret = []
            try:
                res = f(*args, **kwargs)
                ret.append(f'{res}')
            except Exception as e:
                # _trace(e)
                _trace(f.__name__, 'exception', [traceback.format_exc()]) #TODO use , e.__traceback__ like log_error()?

            _trace(f.__name__, 'exit', ret)
        else:
            # Simple execution.
            res = f(*args, **kwargs)

        return res

    return wrapper


#-----------------------------------------------------------------------------------
#---------------------------- Private functions ------------------------------------
#-----------------------------------------------------------------------------------


#---------------------------------------------------------------------------
def _trace(func, line, msgs):
    '''Do one trace record.'''
    elapsed = _get_ns() - _trace_start_time
    msec = elapsed // 1000000
    usec = elapsed // 1000

    parts = []
    parts.append(f'{msec:04}.{usec:03}')
    parts.append(f'{func}:{line}')

    for m in msgs:
        parts.append(f'[{m}]')

    s = ' '.join(parts) + '\n'

    # Write the record. TODO1 if file is locked by other process notify user that trace is one module only.
    _ftrace.write(s)


#---------------------------------------------------------------------------
def _get_ns():
    '''Get current nanosecond.'''
    if platform.system() == 'Darwin':
        log_error('Sorry, we don\'t do Macs')
    elif platform.system() == 'Windows':
        return time.perf_counter_ns()
    else:  # linux variants
        return time.clock_gettime_ns(time.CLOCK_MONOTONIC)

