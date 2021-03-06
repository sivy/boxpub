#  _______  _______  __   __  _______  __   __  _______
# |  _    ||       ||  |_|  ||       ||  | |  ||  _    |
# | |_|   ||   _   ||       ||    _  ||  | |  || |_|   |
# |       ||  | |  | |     | |   |_| ||  |_|  ||       |
# |  _   | |  |_|  | |     | |    ___||       ||  _   |
# | |_|   ||       ||   _   ||   |    |       || |_|   |
# |_______||_______||__| |__||___|    |_______||_______|
#
# Copyright (c) 2014 Steve Ivy <steveivy@gmail.com>
#

import logging
import imp
from datetime import datetime
import jinja2
import markdown
import re
import requests
import dropbox
import json

from dropbox import client, session
# from dropbox.rest import ErrorResponse

from werkzeug.routing import BaseConverter

from flask import Flask, request, make_response

from postutils import split_markdown, process_markdown


CONFIG_FILE = '/etc/boxpub/config.py'

def load_config(config_file):
    try:
        config = imp.load_source('config', config_file)
        return config
    except IOError:
        LOG.critical('Could not load config at %s.' % config_file)
        sys.exit(1)

CONFIG = load_config(CONFIG_FILE)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(module)s.%(funcName)s (%(lineno)d) %(levelname)s: %(message)s'
    )

log = logging.getLogger('boxpub')
format = logging.Formatter(
    '%(asctime)s %(module)s.%(funcName)s (%(lineno)d) %(levelname)s: %(message)s')

fh = logging.FileHandler(CONFIG.LOGFILE)
fh.setLevel(getattr(logging, CONFIG.LOGLEVEL.upper()))

log.addHandler(fh)


boxpub = Flask('boxpub')
boxpub.debug = True


def render_template(template_string, context):
    template_globals = {
        'HOST': request.host,
        # 'PAGE_URL_FULL': request.path_url,
        'QUERY_STRING': request.query_string,
        'URL': request.url,
        'PATH': request.path,
        'settings': CONFIG,
        'config': CONFIG,
        'site': CONFIG.SITE_DATA,
        'time': datetime.now(),
    }

    template_globals.update(context)

    jinja_environment = jinja2.Environment(
        extensions=['jinja2.ext.autoescape'])

    template = jinja_environment.from_string(template_string)

    resp_body = template.render(template_globals)

    return resp_body


def render_file_with_template(target_file, target_template):
    """
    """
    client = dropbox.client.DropboxClient(CONFIG.DROPBOX_PRIVATE_TOKEN)

    file_response, dropbox_meta = client.get_file_and_metadata(
        target_file)

    file_content = file_response.read()

    f = process_markdown(
        target_file, file_content)

    log.debug(f)

    if 'meta' in f:
        fmeta = f['meta']
        fmeta.update(dropbox_meta)
        f['meta'] = fmeta
    else:
        f['meta'] = dropbox_meta

    # data['published'] = data['modified']
    # data['created'] = data['modified']

    # merge 'meta' values with other values
    f.update(f['meta'])

    # fix title
    if 'Title' in f:
        f['title'] = f['Title']

    # permalink
    f['permalink'] = url_for_path(f['path'])

    template_response, meta = client.get_file_and_metadata(
        'templates/%s' % target_template)
    template_content = template_response.read()

    page_content = render_template(template_content, {
            'page': f,
            'post': f,
        })

    return page_content


def url_for_path(path):
    if 'posts' in path:
        year, month, day, filename = re.match(
            '/posts/([\d]{4})-([\d]{2})-([\d]{2})-([\w-]+)\.md',
            path).groups()
        return "/%s/%s/%s/%s" % (year, month, day, filename)
    elif 'page' in path:
        filename = re.match(
            '/pages/([\w-]+)\.md',
            path).group(1)
        return "/pages/%s" % filename

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

boxpub.url_map.converters['regex'] = RegexConverter


############################################################
# web handlers
#
@boxpub.route('/webhooks/dropbox', methods=['GET'])
def dropbox_webhook_verify():
    log.info('Dropbox verification request')
    return request.args.get('challenge')


@boxpub.route('/webhooks/dropbox', methods=['POST'])
def dropbox_webhook_handle():
    log.info('Dropbox post request')
    url = CONFIG.SITE_DATA['url']
    try:
        log.info('PURGING site index')
        purge_resp = requests.request('PURGE', url)
        log.debug(purge_resp.text)
        resp = make_response(purge_resp.text)
    except Exception, e:
        log.exception(e)
        resp = make_response("ERR: " + e.message)
    log.debug(resp)
    return resp


@boxpub.route('/')
def blog_index_handle(template='index.html', content_type='text/html'):
    log.debug('blog_index_handle()')

    target_file = "posts"

    client = dropbox.client.DropboxClient(CONFIG.DROPBOX_PRIVATE_TOKEN)

    dropbox_response = client.metadata(
        target_file, list=True)

    files = dropbox_response['contents']

    files = sorted(
        files,
        key=lambda f: f['path'],
        reverse=True)
    files = files[:10]

    log.debug(files)

    for f in files:
        log.debug(f['path'])

        file_response, dropbox_meta = client.get_file_and_metadata(
            f['path'])

        f.update(dropbox_meta)
        log.debug(f['path'])

        file_content = file_response.read()

        fdata = process_markdown(
            target_file, file_content)

        log.debug(fdata)

        f.update(fdata)
        log.debug(f['path'])

        # fix title
        f.update(f['meta'])
        if 'Title' in f:
            f['title'] = f['Title']

        # permalink
        f['permalink'] = url_for_path(f['path'])

        log.debug(f)

    # log.debug(files)

    template_response, meta = client.get_file_and_metadata(
        'templates/%s' % template)
    template_content = template_response.read()

    page_content = render_template(template_content, {
            'posts': files,
        })

    resp = make_response(page_content)
    resp.headers["Content-Type"] = content_type

    return resp

@boxpub.route('/atom.xml')
def blog_feed_handle(template='atom.xml'):
    return blog_index_handle(template, 'application/atom+xml')


@boxpub.route('/page/<page>')
def blog_page_handle(page, template='post.html'):
    log.debug('blog_page_handle()')

    target_file = "/pages/%s.md" % (page)

    page_content = render_file_with_template(target_file, template)

    return page_content


@boxpub.route('/<regex("[\d]{4}"):year>/<regex("[\d]{2}"):month>/<regex("[\d]{2}"):day>/<filename>')
def blog_post_handle(year, month, day, filename, template='post.html'):
    log.debug('blog_post_handle()')
    log.info('Dropbox post request')

    target_file = "/posts/%s-%s-%s-%s.md" % (year, month, day, filename)

    page_content = render_file_with_template(target_file, template)

    return page_content


if __name__ == "__main__":
    boxpub.run(host='0.0.0.0')
