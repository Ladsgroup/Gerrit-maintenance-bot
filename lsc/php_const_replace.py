from .replacebot import ReplaceBot
import re


class PhpConstReplaceBot(ReplaceBot):
    def __init__(self, old, new, oldclass, newclass):
        oldclass = oldclass.strip('\\')
        newclass = newclass.strip('\\')
        self.search_term = oldclass.split('\\')[-1] + '::' + old
        super().__init__(self.search_term, 'php')
        self.oldclass = oldclass
        self.oldconst = old
        self.newclass = newclass
        self.newconst = new

    def run_replace(self, text):
        if '\nuse {};\n'.format(self.newclass) in text or '\nuse {} as'.format(self.newclass) in text:
            return self.replace_const(text)
        new_text = self.add_use(self.newclass, text)
        if not new_text:
            return text
        return self.replace_const(new_text)
    
    def replace_const(self, text):
        new_text = re.sub(self.search_term, self.newclass.split('\\')[-1] + '::' + self.newconst, text)
        if text.count(self.oldclass.split('\\')[-1]) == 1:
            new_text = new_text.replace('use {};\n'.format(self.oldclass), '')
        return new_text
    
    def add_use(self, newclass, text):
        upper_block = text.split('\nclass ')[0]
        uses = []
        for line in upper_block.split('\n'):
            if line.startswith('use '):
                uses.append(line)
        new_upper_block = upper_block
        for i in range(len(uses)):
            if i == 0:
                continue
            new_upper_block = new_upper_block.replace(uses[i] + '\n', '')
        new_uses = uses.copy()
        new_uses.append('use {};'.format(newclass))
        new_uses = '\n'.join(sorted(new_uses, key=lambda i: i.lower())) + '\n'
        if uses:
            new_upper_block = new_upper_block.replace(uses[0] + '\n', new_uses)
        else:
            if '\n/**' in new_upper_block:
                replace_block = '\n'+ new_uses + '\n/**'
                new_upper_block = replace_block.join(new_upper_block.rsplit('\n/**', 1))
                new_upper_block = new_upper_block.replace('<?php\nuse ', '<?php\n\nuse ', 1)
            else:
                return False
        
        return text.replace(upper_block, new_upper_block, 1)