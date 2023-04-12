import re
from flask import redirect, render_template, url_for


def handle_replace_request(
        replacebot,
        template_name,
        form,
        username,
        allowed_users):
    ticket = form.get('ticket', '').strip()
    commit_message = form.get('commitmessage')
    commit_footer = form.get('commitfooter')
    bumpversion = form.get('bumpversion', '').strip()
    repos = []
    for key in form:
        if key.startswith('mediawiki/') and form[key] == 'on':
            repos.append(key)
    if not repos or not ticket or not commit_message:
        return render_template(
            template_name,
            form=form,
            suggestions=replacebot.get_suggestions(),
            allow=username in allowed_users,
            lang=replacebot.language
        )
    if not re.search(r'^T\d+$', ticket):
        return render_template(
            'done.html',
            result='The ticket does not follow the correct pattern'
        )
    if bumpversion != '0' and not re.search(r'^1\.\d\d(\.\d\d?)?$', bumpversion):
        return render_template(
            'done.html',
            result='The bump version does not follow the correct pattern'
        )
    if username not in allowed_users:
        return redirect(url_for('index'))
    return render_template(
        'done.html',
        result=replacebot.run(
            repos,
            ticket,
            commit_message,
            commit_footer,
            username,
            bumpversion))
