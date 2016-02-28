import requests
import json
from time import sleep
from config import user, password

repository_url = 'https://api.github.com/repositories'

def request_to_github(url):
    print('requesting %s...' % url)
    r = requests.get(url, auth=(user, password))
    if r.headers['X-RateLimit-Remaining'] == 0:
        print('lololol Github screws you')
        sleep(3600)
        r = requests.get(url, auth=(user, password))
    return r


def get_forks(repo):
    ret = []
    r = request_to_github(repo['forks_url'])
    forks = r.json()
    ret.extend(forks)
    for repo in forks:
        ret.extend(get_forks(repo))
    return ret

if __name__ == '__main__':
    counter = 0
    next_url = repository_url
    while (next_url != None and counter < 1000):
        r = request_to_github(next_url)
        if 'next' in r.links and 'url' in r.links['next']:
            next_url = r.links['next']['url']
        else:
            next_url = None
        for repo in r.json():
            if repo['fork']:
                counter += 1
