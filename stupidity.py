import requests
import json
from time import sleep
from config import user, password

session = requests.Session()

repository_url = 'https://api.github.com/repositories'
search_url = 'https://api.github.com/search/repositories?q=user:%s+repo:%s'

def request_to_github(url):
    print('requesting %s...' % url)
    r = session.get(url, auth=(user, password))
    if r.headers['X-RateLimit-Remaining'] == 0:
        print('lololol Github screws you')
        sleep(3600)
        r = session.get(url, auth=(user, password))
    return r

def iter_seq(iterable):
    if isinstance(iterable, list):
        return iterable
    elif isinstance(iterable, dict):
        return list(iterable.items())

def get_all(url, total=float('inf')):
    counter = 0
    next_url = url
    # while there is a next page and #elems is < total
    while (next_url != None and counter < total):
        r = request_to_github(next_url)
        # check if next page
        if 'next' in r.links and 'url' in r.links['next']:
            next_url = r.links['next']['url']
        else:
            next_url = None
        # yield every elem of page and increase #elems
        res = r.json()
        for elem in iter_seq(res):
            if counter >= total:
                break
            yield elem
            counter += 1

def get_repo(full_name):
    user, repo = full_name.split('/')
    search = request_to_github(search_url % (user, repo)).json()
    for r in search['items']:
        if r['full_name'] == full_name:
            return r
    return None

def get_forks(repo):
    return get_repo(repo['full_name'])['forks_count']

def get_stargazers(repo):
    return get_repo(repo['full_name'])['stargazers_count']

def get_languages(repo):
    languages = list(get_all(repo['languages_url']))
    return languages

if __name__ == '__main__':
    for repo in get_all(repository_url, 1):
        if not repo['fork']:
            print(get_forks(repo))
            print(get_stargazers(repo))
            print(get_languages(repo))
            pass

