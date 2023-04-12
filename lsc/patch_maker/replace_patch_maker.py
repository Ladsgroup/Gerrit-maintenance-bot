import json
from collections import OrderedDict
from packaging import version
from .gerrit import GerritBot

username_mapping = {
    'DKinzler (WMF)': 'daniel-kinzler',
    'Volker E. (WMF)': 'volker-e'
}

def bump_minimum_version_in_json(bump_version, content):
    requires = content.get('requires', {})
    ver = requires.get('MediaWiki', '>= 1.0.0').split(' ')[-1]
    if bump_version.count('.') < 2:
        bump_version += '.0'
    if ver.count('.') < 2:
        ver += '.0'
    if version.parse(bump_version) <= version.parse(ver):
        return
    requires['MediaWiki'] = '>= ' + bump_version
    content['requires'] = requires
    return content


class ReplacePatchMaker(GerritBot):
    def __init__(self, repo, commit_message, files, replacer, ticket, username, bump_version):
        self.replacer = replacer
        self.files = files
        self.ticket = ticket
        self.username = username
        self.bump_version = bump_version
        super().__init__(repo, commit_message, ticket)

    def changes(self):
        if self.bump_version and self.bump_version != '0':
            self._bump_minimum_version()
        for file in self.files:
            with open(file, 'r') as f:
                content = f.read()
            with open(file, 'w') as f:
                f.write(self.replacer.run_replace(content))

    def normalized_username(self):
        if self.username in username_mapping:
            return username_mapping[self.username].lower()
        return self.username.lower().replace(' ', '_')

    def commit(self):
        self.check_call(['git', 'add', '.'])
        with open('.git/COMMIT_EDITMSG', 'w') as f:
            f.write(self.commit_message)
        self.check_call(['git', 'commit', '-F', '.git/COMMIT_EDITMSG'])
        self.check_call(self.build_push_command(
            {
                'repo': self.name,
                'hashtags': ['lsc', 'lsc-requested-by-' + self.normalized_username()]
            },
            self.ticket))
    
    def _bump_minimum_version(self):
        for file_name in ['extension.json', 'skin.json']:
            try:
                with open(file_name, 'r') as f:
                    content = json.loads(f.read(), object_pairs_hook=OrderedDict)
            except:
                continue
            else:
                # Todo: Better name, I'm too tired right now
                actual_file_name = file_name
                break
        else:
            return
        content = bump_minimum_version_in_json(self.bump_version, content)

        with open(actual_file_name, 'w') as f:
            f.write(json.dumps(content, indent='\t'))
