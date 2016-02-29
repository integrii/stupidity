import requests
from tqdm import tqdm
import json
from time import sleep
from collections import defaultdict
from config import user, password
import sys

session = requests.Session()

repository_url = 'https://api.github.com/repositories'
repo_url = 'https://api.github.com/repos/%s/%s'
cache_file = 'cache.json'

# CACHING
def write_progression(counter, url):
    # if cache exists
    try:
        data = read_cache()
    except:
        data = {}
    data['counter'] = counter
    data['url'] = url
    with open(cache_file, 'w') as f:
        json.dump(data, f)

def write_result(result):
    try:
        data = read_cache()
    except:
        data = {}
    data['result'] = result
    with open(cache_file, 'w') as f:
        json.dump(data, f)

def read_cache():
    return json.load(open(cache_file))

# REQUESTING
def request_to_github(url):
    """ return ´url´ HTTP response and sleep if rate-limit is reached """
    print('requesting %s...' % url)
    r = None
    while (r == None):
        r = session.get(url, auth=(user, password))
        print('rate-limit: %s' % r.headers['X-RateLimit-Remaining'])
        if r.headers['X-RateLimit-Remaining'] == "0":
            print('LOLOLOL Github screws you')
            sleep(60)
            r = None
    return r

def get_all(url, total=float('inf'), beg=0):
    """ yield ´total´ elements + progression from ´url´ beginning at ´beg+1´ element, abstracting paging"""
    next_url = url
    counter = 0
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
            if counter > beg:
                yield elem, counter, url
            counter += 1

def get_all_repo(total=float('inf')):
    """ yield ´total´ repos reading cache before (to know progression) and updating cache """
    try:
        data = read_cache()
        url = data['url']
        counter = data['counter']
    except:
        url = repository_url
        counter = 0
    for repo, counter, url in get_all(url, total, counter):
        yield repo
        write_progression(counter, url)

def get_all_elem(url):
    """ yield only elements of ´url´ discarding progression """
    for repo, counter, url in get_all(url):
        yield repo

def get_full_repo(repo):
    """ return full repo metadata given the partial info from repos list"""
    user, repo = repo['full_name'].split('/')
    return request_to_github(repo_url % (user, repo)).json()

# MODEL
def get_forks(full_repo):
    """ return #forks of ´full_repo´ """
    return full_repo['forks_count']

def get_stargazers(full_repo):
    """ return #stars of ´full_repo´ """
    return full_repo['stargazers_count']

def get_contributors(repo):
    """ return #contributors of ´repo´ by crawling them all. May consumes a lot of time """
    return len(list(get_all_elem(repo['contributors_url'])))

def get_languages(repo):
    """ return ratio of each language used in ´repo´ as a dict 'language': ratio """
    languages = list(get_all_elem(repo['languages_url']))
    total = sum([x[1] for x in languages])
    return {l: n/total for l, n in languages}

def stupidity(f, s, c):
    """ compute stupidity ratio from #forks, #stars, #contributors """
    return 100 * (f - c)/s

def repo_stupidity(res, repo):
    """ compute stupidity ratio for ´repo´ and update languages in ´res´ depending on language ratio in ´repo´ """
    full_repo = get_full_repo(repo)
    nforks = get_forks(full_repo)
    nstars = get_stargazers(full_repo)
    ncontrib = get_contributors(repo)
    languages = get_languages(repo)
    magic = stupidity(nforks, nstars, ncontrib)
    if magic >= 0:
        for lang, ratio in languages.items():
            res[lang][0] = (res[lang][0] * res[lang][1] + magic * ratio) / (res[lang][1] + 1)
            res[lang][1] += 1

# UTILITIES
def iter_seq(iterable):
    if isinstance(iterable, list):
        return iterable
    elif isinstance(iterable, dict):
        return list(iterable.items())

def pretty_print(res):
    for lang, data in res.items():
        if data[1] >= 5:
            print("Language: %-*s Stupidity ratio: %-*f Number of projects: %-*d" % (20, lang, 10, data[0], 10, data[1]))

if __name__ == '__main__':
    try:
        n = int(sys.argv[1])
    except ValueError:
        print('Usage: %s <number of repos>' % argv[0])
    try:
        result = defaultdict(lambda: [0,0], read_cache()['result'])
    except:
        result = defaultdict(lambda: [0,0])
    for repo in tqdm(get_all_repo(n)):
        if not repo['fork']:
            try:
                repo_stupidity(result, repo)
            except KeyError:
                pass
            except json.decoder.JSONDecodeError:
                pass
            except ZeroDivisionError:
                pass
            write_result(result)
    pretty_print(result)

