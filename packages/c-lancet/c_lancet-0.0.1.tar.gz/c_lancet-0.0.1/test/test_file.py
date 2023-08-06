import sys
sys.path.append('..')
from clancet.file import CFile


def test_get_func():
    cf = CFile()
    cf.set_path('../testcase/apps/x509.c')
    func = cf.get_func()
    assert(len(func) == 9)

    print(func[0].get_name())
    print(func[0].get_type())
    print(func[0].get_para())


if __name__ == '__main__':
    test_get_func()