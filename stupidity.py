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

def request_to_github(url):
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

def iter_seq(iterable):
    if isinstance(iterable, list):
        return iterable
    elif isinstance(iterable, dict):
        return list(iterable.items())

def get_all(url, total=float('inf'), beg=0):
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

def get_all_repo(default_url, total=float('inf')):
    try:
        data = read_cache()
        url = data['url']
        counter = data['counter']
    except:
        url = default_url
        counter = 0
    for repo, counter, url in get_all(url, total, counter):
        yield repo
        write_progression(counter, url)

def get_all_elem(url):
    for repo, counter, url in get_all(url):
        yield repo

def get_repo(repo):
    user, repo = repo['full_name'].split('/')
    return request_to_github(repo_url % (user, repo)).json()

def get_forks(repo):
    return repo['forks_count']

def get_stargazers(repo):
    return repo['stargazers_count']

def get_contributors(repo):
    return len(list(get_all_elem(repo['contributors_url'])))

def get_languages(repo):
    languages = list(get_all_elem(repo['languages_url']))
    total = sum([x[1] for x in languages])
    return {l: n/total for l, n in languages}

def magic_formula(f, s, c):
    return 100 * (f - c)/s

def pretty_print(res):
    for lang, data in res.items():
        if data[1] >= 5:
            print("Language: %-*s Stupidity ratio: %-*f Number of projects: %-*d" % (20, lang, 10, data[0], 10, data[1]))

def magic_repo(res, repo):
    full_repo = get_repo(repo)
    nforks = get_forks(full_repo)
    nstars = get_stargazers(full_repo)
    ncontrib = get_contributors(repo)
    languages = get_languages(repo)
    magic = magic_formula(nforks, nstars, ncontrib)
    if magic >= 0:
        for lang, ratio in languages.items():
            res[lang][0] = (res[lang][0] * res[lang][1] + magic * ratio) / (res[lang][1] + 1)
            res[lang][1] += 1


if __name__ == '__main__':
    try:
        n = int(sys.argv[1])
    except ValueError:
        print('Usage: %s <number of repos>' % argv[0])
    try:
        DATRESULT = defaultdict(lambda: [0,0], read_cache()['result'])
    except:
        DATRESULT = defaultdict(lambda: [0,0])
    for repo in tqdm(get_all_repo(repository_url, n)):
        if not repo['fork']:
            try:
                magic_repo(DATRESULT, repo)
            except KeyError:
                pass
            except json.decoder.JSONDecodeError:
                pass
            except ZeroDivisionError:
                pass
            write_result(DATRESULT)
    pretty_print(DATRESULT)

