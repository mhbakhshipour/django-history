from threading import current_thread


def current_request():
    _requests = {}
    return _requests.get(current_thread().ident, None)
