from app import fibo


def test_fibo():
    assert(fibo(10) == 55)
    assert(fibo(1) == 1)
    assert(fibo(0) == 0)
