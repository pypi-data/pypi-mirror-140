import ghstack.github

def main(github: ghstack.github.GitHubEndpoint):
    ns = github.get('notifications', all=True, per_page=100, page=1)
    for n in ns:
        from pprint import pprint
        pprint(n)
        #print("{} {}".format(n['subject']['title'], n['url']))
        break
