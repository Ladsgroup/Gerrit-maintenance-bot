import re
import sys

from gerrit import GerritBot


class PuppetDisableNotificationPatchMaker(GerritBot):
    def __init__(self, dbname, bug_id):
        self.dbname = dbname
        super().__init__(
            'operations/puppet',
            '{}: Disable notifications\n\nReimage to bullseye\n\nBug:{}'.format(
                dbname,
                bug_id))

    def changes(self):
        with open('hieradata/hosts/{}.yaml'.format(self.dbname), 'a') as f:
            f.write('\nprofile::monitoring::notifications_enabled: false\n')

    def commit(self):
        self.check_call(['git', 'add', '.'])
        with open('.git/COMMIT_EDITMSG', 'w') as f:
            f.write(self.commit_message)
        self.check_call(['git', 'commit', '-F', '.git/COMMIT_EDITMSG'])
        self.check_call(self.build_push_command(
            {'repo': self.name, 'branch': 'production'}))


maker = PuppetDisableNotificationPatchMaker(
    re.findall(r'(db\d+)', ' '.join(sys.argv))[0],
    re.findall(r'(T\d+)', ' '.join(sys.argv))[0]
)
maker.run()
