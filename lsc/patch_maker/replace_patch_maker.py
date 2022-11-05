from .gerrit import GerritBot

username_mapping = {
    'DKinzler (WMF)': 'daniel-kinzler',
    'Volker E. (WMF)': 'volker-e'
}


class ReplacePatchMaker(GerritBot):
    def __init__(self, repo, commit_message, files, replacer, ticket, username):
        self.replacer = replacer
        self.files = files
        self.ticket = ticket
        self.username = username
        super().__init__(repo, commit_message, ticket)

    def changes(self):
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
