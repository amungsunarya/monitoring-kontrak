def test_login_page_accessible(client):
    r = client.get('/login')
    assert r.status_code == 200
    assert b'Login' in r.data or b'login' in r.data


def test_login_gagal(client):
    r = client.post('/login', data={
        'username': 'salah',
        'password': 'salah'
    }, follow_redirects=True)
    assert r.status_code == 200


def test_dashboard_redirect_tanpa_login(client):
    r = client.get('/dashboard/', follow_redirects=False)
    assert r.status_code == 302
    assert '/login' in r.location


def test_kontrak_redirect_tanpa_login(client):
    r = client.get('/kontrak/', follow_redirects=False)
    assert r.status_code == 302