from flask import Flask, render_template, request
from lsc.php_const_replace import PhpConstReplaceBot

app = Flask(__name__)

from lsc.replacebot import SimpleReplaceBot


@app.route("/")
def hello():
    return render_template('home.html')

@app.route("/php", methods=['GET'])
def bacc():
    return render_template('php.html')


@app.route("/php/simple-replace", methods=['GET'])
def php_simple_replace():
    return render_template('php_simple_replace.html')

@app.route("/php/simple-replace", methods=['POST'])
def php_simple_replace_post():
    old = request.form['old'].strip()
    new = request.form['new'].strip()
    ticket = request.form.get('ticket')
    commit_message = request.form.get('commitmessage')
    replacebot = SimpleReplaceBot(old, new, 'php')
    repos = []
    for key in request.form:
        if key.startswith('mediawiki/') and request.form[key] == 'on':
            repos.append(key)
    if not repos or not ticket or not commit_message:
        return render_template(
            'php_simple_replace_with_repos.html',
            old=old,
            new=new,
            suggestions=replacebot.get_suggestions()
        )
    return render_template(
        'done.html',
        result=replacebot.run(repos, ticket, commit_message)
    )

@app.route("/php/const-replace", methods=['GET'])
def php_const_replace():
    return render_template('php_const_replace.html')

@app.route("/php/const-replace", methods=['POST'])
def php_const_replace_post():
    old = request.form['old'].strip()
    oldclass = request.form['oldclass'].strip()
    new = request.form['new'].strip()
    newclass = request.form['newclass'].strip()
    ticket = request.form.get('ticket')
    commit_message = request.form.get('commitmessage')
    replacebot = PhpConstReplaceBot(old, new, oldclass, newclass)
    repos = []
    for key in request.form:
        if key.startswith('mediawiki/') and request.form[key] == 'on':
            repos.append(key)
    if not repos or not ticket or not commit_message:
        return render_template(
            'php_const_replace_with_repos.html',
            old=old,
            oldclass=oldclass,
            new=new,
            newclass=newclass,
            suggestions=replacebot.get_suggestions()
        )
    return render_template(
        'done.html',
        result=replacebot.run(repos, ticket, commit_message)
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0')
