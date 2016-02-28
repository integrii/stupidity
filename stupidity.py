import requests
import json
from config import user, password

repository_url = "https://api.github.com/repositories"

next_url = repository_url

# def get_forks(url):

counter = 0

while (next_url != None and counter < 1000):
    # print(next_url)
    repositories = requests.get(next_url, auth=(user, password))
    if 'next' in repositories.links and 'url' in repositories.links['next']:
        next_url = repositories.links['next']['url']
    else:
        next_url = None
    print(repositories.json())
    for repo in repositories.json():
        if repo['fork']:
            print(repo['full_name'])
            counter += 1
