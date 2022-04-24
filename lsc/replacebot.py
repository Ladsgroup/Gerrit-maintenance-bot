from difflib import HtmlDiff
import re
from collections import defaultdict

from lsc.patch_maker import replace_patch_maker

from .gerrit import get_file_from_gerrit
import requests
import urllib.parse

class ReplaceBot(object):
    def __init__(self, old, language):
        super().__init__()
        self.old = old
        self.language = language

    def get_suggestions(self):
        suggestions = defaultdict(list)
        for case in self.get_matches():
            match, repo = case
            file_name = match['Filename']
            print(repo, file_name)
            file_content = get_file_from_gerrit(repo, file_name)
            new_file_content = self.run_replace(file_content)
            if file_content == new_file_content:
                continue
            diff = HtmlDiff().make_table(
                file_content.split('\n'),
                new_file_content.split('\n'),
                context=True
            )
            suggestions[repo].append((file_name, diff))

        return suggestions

    def run_replace(self, text):
        raise NotImplementedError

    def get_matches(self, repos = []):
        q = urllib.parse.quote(self.old, safe="")
        data = requests.get(
            'https://codesearch.wmcloud.org/deployed/api/v1/search?stats=fosho&repos=*&files=\.{}&rng=%3A&q={}&files=&excludeFiles=&i=nope'.format(self.language, q)).json()
        suggestions = {}
        for repo in data['Results']:
            if repos and repo not in repos:
                continue
            if not repo.startswith('mediawiki/extensions/') and not repo.startswith('mediawiki/skins/'):
                continue
            suggestions[repo] = []
            for match in data['Results'][repo]['Matches']:
                yield (match, repo)


    def run(self, repos, ticket, commit_message, commit_footer = '', username = ''):
        cases = defaultdict(list)
        for case in self.get_matches(repos):
            match, repo = case
            file_name = match['Filename']
            cases[repo].append(file_name)
        if commit_footer:
            commit_footer = '\n' + commit_footer.strip('\n')
        
        for repo in cases:
            patch_maker = replace_patch_maker.ReplacePatchMaker(
                repo,
                commit_message.strip('\n').strip() + '\n\nBug: ' + ticket + commit_footer, 
                cases[repo],
                self,
                ticket,
                username
            )
            patch_maker.run()

        return 'Done?<br><a href="https://gerrit.wikimedia.org/r/q/topic:%2522lsc-{}%2522">See the result</a>'.format(ticket)


class SimpleReplaceBot(ReplaceBot):
    def __init__(self, old, new, language):
        super().__init__(old, language)
        self.new = new

    def run_replace(self, text):
        return re.sub(self.old, self.new, text)
