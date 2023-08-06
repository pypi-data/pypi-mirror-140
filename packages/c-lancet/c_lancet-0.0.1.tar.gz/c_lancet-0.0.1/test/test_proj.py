import sys
sys.path.append('..')
from clancet.proj import CProj


def test_count_ext():
    cp = CProj(proj_path = '../testcase/apps/')
    res = cp.count_ext()
    assert(res['c'] == 75)
    assert(res['h'] == 18)


if __name__ == '__main__':
    test_count_ext()