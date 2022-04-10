from .gerrit import GerritBot


class ReplacePatchMaker(GerritBot):
    def __init__(self, repo, commit_message, files, replacer, ticket):
        self.replacer = replacer
        self.files = files
        self.ticket = ticket
        super().__init__(repo, commit_message, ticket)

    def changes(self):
        for file in self.files:
            with open(file, 'r') as f:
                content = f.read()
            with open(file, 'w') as f:
                f.write(self.replacer.run_replace(content))

    def commit(self):
        self.check_call(['git', 'add', '.'])
        with open('.git/COMMIT_EDITMSG', 'w') as f:
            f.write(self.commit_message)
        self.check_call(['git', 'commit', '-F', '.git/COMMIT_EDITMSG'])
        self.check_call(self.build_push_command(
            {'repo': self.name, 'hashtags': ['lsc']}, self.ticket))
