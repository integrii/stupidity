# Goal

This project samples repositories from github and use the equation described in http://ericgreer.info/github/funny/stupidity/2016/02/28/judging-the-stupidity-of-github-projects.html to measure the stupidity of users of each repo.
It then look for the languages of this repo and make an average of stupidity by language.
So useful, or not.

# Use (Python 3)

* pip install -r requirements.txt
* copy "config.py.sample" to "config.py" and fill in user and password
* python3 stupidity.py \<number of repos\>

Everything is cached automatically.