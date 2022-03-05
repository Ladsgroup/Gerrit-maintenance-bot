import sys

import requests

from gerrit import GerritBot


class ReplaceInRepoBot(GerritBot):
    def __init__(self, repo, commit_message, old, new, files):
        self.old = old
        self.new = new
        self.files = files
        super().__init__(repo, commit_message)

    def changes(self):
        for file in self.files:
            with open(file, 'r') as f:
                content = f.read()
            with open(file, 'w') as f:
                f.write(content.replace(self.old, self.new))

    def commit(self):
        self.check_call(['git', 'add', '.'])
        with open('.git/COMMIT_EDITMSG', 'w') as f:
            f.write(self.commit_message)
        self.check_call(['git', 'commit', '-F', '.git/COMMIT_EDITMSG'])
        self.check_call(self.build_push_command(
            {'repo': self.name}))


class ReplaceBot(object):
    def __init__(self, commit_message, old, new):
        self.commit_message = commit_message
        self.old = old
        self.new = new

    def run(self):
        data = requests.get(
            'https://codesearch.wmflabs.org/deployed/api/v1/search?stats=fosho&repos=*&rng=:20&q=\\b{}\\b&i=fosho'.format(self.old)).json()

        if not data.get('Results'):
            # print(config)
            return
        repos = []
        for repo in data['Results']:
            repos.append(repo)
        which_repos = input(
            'Which repos do you want, put the numbers comma sep? ' +
            ', '.join(
                [
                    '{} ({})'.format(
                        repos[i],
                        i) for i in range(
                        len(repos))]))
        which_repos = [int(i.strip()) for i in which_repos.strip().split(',')]
        for i in which_repos:
            repo_name = repos[i]
            repo_search_data = data['Results'][repo_name]
            files = [i['Filename'] for i in repo_search_data['Matches']]
            if not files:
                continue
            bot = ReplaceInRepoBot(
                repo_name,
                self.commit_message,
                self.old,
                self.new,
                files)
            bot.run()


maker = ReplaceBot(
    'Change use of deprecated getLazyConnectionRef\n\nBug: T255493',
    'getLazyConnectionRef',
    'getConnectionRef')
maker.run()
