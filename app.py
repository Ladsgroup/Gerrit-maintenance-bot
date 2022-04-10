import json
import os
from functools import wraps

import flask
import mwoauth
from flask import Flask, render_template, request
from flask_session import Session

from lsc.php_const_replace import PhpConstReplaceBot
from lsc.replacebot import SimpleReplaceBot

app = Flask(__name__)
app = flask.Flask(__name__)
__dir__ = os.path.dirname(__file__)
app.config.update(json.load(open(os.path.join(__dir__, 'config.json'))))
Session(app)


def authenticated(f):
    @wraps(f)
    def wrapped_f(*args, **kwargs):
        if 'username' in flask.session:
            return f(*args, **kwargs)
        else:
            return 'Nope'

    return wrapped_f


@app.route('/auth/login')
def login():
    """Initiate an OAuth login.

    Call the MediaWiki server to get request secrets and then redirect the
    user to the MediaWiki server to sign the request.
    """
    consumer_token = mwoauth.ConsumerToken(
        app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])
    try:
        redirect, request_token = mwoauth.initiate(
            app.config['OAUTH_MWURI'], consumer_token)
    except Exception:
        app.logger.exception('mwoauth.initiate failed')
        return flask.redirect(flask.url_for('index'))
    else:
        flask.session['request_token'] = dict(zip(
            request_token._fields, request_token))
        return flask.redirect(redirect)


@app.route('/auth/oauth-callback')
def oauth_callback():
    """OAuth handshake callback."""
    if 'request_token' not in flask.session:
        flask.flash(u'OAuth callback failed. Are cookies disabled?')
        return flask.redirect(flask.url_for('index'))

    consumer_token = mwoauth.ConsumerToken(
        app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])

    try:
        access_token = mwoauth.complete(
            app.config['OAUTH_MWURI'],
            consumer_token,
            mwoauth.RequestToken(**flask.session['request_token']),
            flask.request.query_string)

        identity = mwoauth.identify(
            app.config['OAUTH_MWURI'], consumer_token, access_token)
    except Exception:
        app.logger.exception('OAuth authentication failed')

    else:
        flask.session['access_token'] = dict(zip(
            access_token._fields, access_token))
        flask.session['username'] = identity['username']
    return flask.redirect(flask.url_for('index'))


@app.route('/auth/logout')
def logout():
    """Log the user out by clearing their session."""
    flask.session.clear()
    return flask.redirect(flask.url_for('index'))


@app.route("/")
def index():
    return render_template('home.html', username=flask.session.get('username'))


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
    if flask.session['username'] not in app.config['allowed_users']:
        return flask.redirect(flask.url_for('index'))
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
    if flask.session['username'] not in app.config['allowed_users']:
        return flask.redirect(flask.url_for('index'))
    return render_template(
        'done.html',
        result=replacebot.run(repos, ticket, commit_message)
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0')
