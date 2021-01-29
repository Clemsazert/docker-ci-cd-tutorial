from app import app

tester = app.test_client()


def test_healthcheck():
    response = tester.get('/', content_type='html/text')
    assert(response.status_code == 200)
    assert(response.data == b'Hello, World!')


def test_fibo_route():
    response = tester.get('/fibo/10', content_type='html/text')
    assert(response.status_code == 200)
    assert(response.data == b'{"result":55}\n')
