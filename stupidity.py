import requests
import requests_cache
from tqdm import tqdm
import json
from time import sleep, time
from collections import defaultdict
from config import user, password
import sys

# requests_cache.install_cache()
session = requests.Session()

repository_url = 'https://api.github.com/repositories'
search_url = 'https://api.github.com/search/repositories?q=user:%s+repo:%s+%s'

def request_to_github(url):
    print('requesting %s...' % url)
    r = None
    while (r == None):
        r = session.get(url, auth=(user, password))
        print('rate-limit: %s' % r.headers['X-RateLimit-Remaining'])
        if r.headers['X-RateLimit-Remaining'] == "0":
            print('lololol Github screws you')
            timediff = time() - request_to_github.time
            print(timediff)
            sleep(60-timediff)
            request_to_github.time = time()
            r = None
    return r

request_to_github.time = time()

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
    search = request_to_github(search_url % (user, repo, repo)).json()
    for r in search['items']:
        if r['full_name'] == full_name:
            return r
    return None

def get_forks(repo):
    return get_repo(repo['full_name'])['forks_count']

def get_stargazers(repo):
    return get_repo(repo['full_name'])['stargazers_count']

def get_contributors(repo):
    return len(list(get_all(repo['contributors_url'])))

def get_languages(repo):
    languages = list(get_all(repo['languages_url']))
    total = sum([x[1] for x in languages])
    return {l: n/total for l, n in languages}

def magic_formula(f, s, c):
    return 100 * (f - c)/s

def pretty_print(res):
    for lang, data in res.items():
        print("Language: %-*s Stupidity ratio: %-*f Number of projects: %-*d" % (20, lang, 10, data[0], 10, data[1]))

if __name__ == '__main__':
    try:
        n = int(sys.argv[1])
    except ValueError:
        print('Usage: %s <number of repos>' % argv[0])
    DATRESULT = defaultdict(lambda: [0,0])
    for repo in tqdm(get_all(repository_url, n)):
        if not repo['fork']:
            nforks = get_forks(repo)
            nstars = get_stargazers(repo)
            ncontrib = get_contributors(repo)
            languages = get_languages(repo)
            magic = magic_formula(nforks, nstars, ncontrib)
            if magic >= 0:
                for lang, ratio in languages.items():
                    DATRESULT[lang][0] = (DATRESULT[lang][0] * DATRESULT[lang][1] + magic * ratio) / (DATRESULT[lang][1] + 1)
                    DATRESULT[lang][1] += 1
    pretty_print(DATRESULT)

