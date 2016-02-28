import requests
import json
from time import sleep
from config import user, password

session = requests.Session()

repository_url = 'https://api.github.com/repositories'

def request_to_github(url):
    print('requesting %s...' % url)
    r = session.get(url, auth=(user, password))
    if r.headers['X-RateLimit-Remaining'] == 0:
        print('lololol Github screws you')
        sleep(3600)
        r = session.get(url, auth=(user, password))
    return r

def get_all(url, total=float('inf')):
    counter = 0
    next_url = url
    # while there is a next page and #elems is < total
    while (next_url != None and counter <= total ):
        r = request_to_github(next_url)
        # check if next page
        if 'next' in r.links and 'url' in r.links['next']:
            next_url = r.links['next']['url']
        else:
            next_url = None
        # yield every elem of page and increase #elems
        res = r.json()
        counter += len(res)
        for elem in res:
            yield elem

def get_forks(repo):
    ret = []
    forks = get_all(repo['forks_url'])
    for repo in forks:
        ret.append(repo)
        ret.extend(get_forks(repo))
    return ret

if __name__ == '__main__':
    for repo in get_all(repository_url, 100):
        if not repo['fork']:
            forks = get_forks(repo)
            print(len(forks))
            break

