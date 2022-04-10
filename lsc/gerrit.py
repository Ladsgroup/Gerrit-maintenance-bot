import base64

import requests


def get_gerrit_path(repo, filename):
    return repo + '/+/master/' + filename


def get_file_from_gerrit(repo, filename):
    gerrit_url = 'https://gerrit.wikimedia.org/g/'
    url = gerrit_url + '{0}?format=TEXT'.format(get_gerrit_path(repo, filename))
    r = requests.get(url)
    if r.status_code == 200:
        return base64.b64decode(r.text).decode('utf-8')
    else:
        return ''