
import sbot_common_master as sc


#-------------------------- trace test code --------------------------------------

class a_test_class(object):
    def __init__(self, arg):
        T(f'making a class:{arg}')
        self._arg = arg

    @traced_function
    def test_class_do_something(self, arg2):
        res = f'{self._arg}-glom-{arg2}'
        return res


def a_traceless_function(s):
    T(f'I got this:{s}')


@traced_function
def a_test_function(a1: int, a2: float):
    cl1 = a_test_class(a1)
    cl2 = a_test_class(a2)
    T(f'function:{a1 + a2}')
    ret = f'answer is cl1:{cl1.test_class_do_something(a1)}...cl2:{cl2.test_class_do_something(a2)}'
    return ret


@traced_function
def do_a_suite():
    '''Do a test suite.'''
    T('something sweet')
    ret = a_test_function(5, 9.126)
    # error_function(0)
    a_traceless_function('help!')
    return ret


@traced_function
def error_function(denom):
    return 1 / denom


#-------------------------- test start here --------------------------------

sc.start_trace()

time_str = f'{str(datetime.datetime.now())}'[0:-3]
T(f'>>>>>>>> Start test {time_str}')
do_a_suite()
T(do_a_suite.__name__)
T(do_a_suite.__doc__)

sc.stop_trace()
