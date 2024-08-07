import sys
import datetime
from .tracker import *  # noqa: F403


#-------------------------- trace test code --------------------------------------

class TestClass(object):
    name: str
    tags: []

    def __init__(self, name, tags, arg):
        T('making one TestClass', name, tags, arg)
        self._name = name
        self._tags = tags
        self._arg = arg

    @traced_function
    def test_class_do_something(self, arg2):
        res = f'{self._arg}-glom-{arg2}'  #OK user formatted string
        return res

    def __str__(self):
        '''Needed for trace.'''
        s = f'TestClass:{self._name} tags:{self._tags} arg:{self._arg}'
        return s

def a_traceless_function(s):
    T(f'I got this => "{s}"')


@traced_function
def another_test_function(a_list, a_dict):
    return len(a_list) + len(a_dict)


@traced_function
def a_test_function(a1: int, a2: float):
    cl1 = TestClass('number 1', [45, 78, 23], a1)
    T(cl1)
    cl2 = TestClass('number 2', [100, 101, 102], a2)
    T(cl2)
    ret = f'answer is cl1:{cl1.test_class_do_something(a1)}...cl2:{cl2.test_class_do_something(a2)}'
    return ret


@traced_function
def do_a_suite(alpha, nuber):
    '''Make a nice suite.'''
    T('something sweet')
    # T(a_test_function(5, 9.126))
    ret = a_test_function(5, 9.126)
    # error_function(0)
    a_traceless_function('can you see me?')
    ret = another_test_function([33, 'tyu', 3.56], {'aaa': 111, 'bbb': 222, 'ccc': 333})
    return ret


@traced_function
def error_function(denom):
    '''Cause esception.'''
    return 1 / denom


#-------------------------- test start here --------------------------------

def do_it():

    trace_fn = os.path.join(os.path.dirname(__file__), 'tracker.log')
    # trace_fn = sc.get_store_fn(f'trace_{log_name}.log') TODO support more than one at a time? Doesn't seem useful.

    start_trace(trace_fn)

    time_str = f'{str(datetime.datetime.now())}'[0:-3]
    T(f'!!! Start test at', time_str)
    do_a_suite(nuber=911, alpha='abcd')  # named args
    # T(do_a_suite.__name__)
    # T(do_a_suite.__doc__)

    stop_trace()
    
do_it()
