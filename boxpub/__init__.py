import logging
import config
from datetime import datetime
import jinja2
import markdown

import dropbox
from dropbox import client, session
# from dropbox.rest import ErrorResponse

from werkzeug.routing import BaseConverter

from flask import Flask, request

from postutils import split_markdown, process_markdown


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(module)s.%(funcName)s (%(lineno)d) %(levelname)s: %(message)s'
    )
log = logging.getLogger('boxpub')


boxpub = Flask('boxpub')
boxpub.debug = True


def render_template(template_string, context):
    template_globals = {
        'HOST': request.host,
        # 'PAGE_URL_FULL': request.path_url,
        'QUERY_STRING': request.query_string,
        'URL': request.url,
        'PATH': request.path,
        'settings': config,
        'config': config,
        'site': {
            'title': 'monkinetic',
            'subhead': '',
            'description': '',
            'url': '',
            'time': datetime.now(),
        },
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
    client = dropbox.client.DropboxClient(config.DROPBOX_PRIVATE_TOKEN)

    file_response, dropbox_meta = client.get_file_and_metadata(
        target_file)

    file_content = file_response.read()

    fdata = process_markdown(
        target_file, file_content)

    log.debug(fdata)

    if 'meta' in fdata:
        fmeta = fdata['meta']
        fmeta.update(dropbox_meta)
        if 'Title' in fmeta:
            fmeta['title'] = fmeta['Title']
        fdata['meta'] = fmeta
    else:
        fdata['meta'] = dropbox_meta

    # data['published'] = data['modified']
    # data['created'] = data['modified']

    template_response, meta = client.get_file_and_metadata(
        'templates/%s' % target_template)
    template_content = template_response.read()

    page_content = render_template(template_content, {
            'page': fdata,
            'post': fdata,
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
    return ""


@boxpub.route('/')
def blog_index_handle(template='index.html'):
    log.debug('blog_index_handle()')

    target_file = "posts"

    client = dropbox.client.DropboxClient(config.DROPBOX_PRIVATE_TOKEN)

    dropbox_meta = client.metadata(
        target_file, list=True)

    log.info('files: %s' % len(dropbox_meta['contents']))

    files = dropbox_meta['contents']

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

        file_content = file_response.read()

        fdata = process_markdown(
            target_file, file_content)

        log.debug(fdata)

        f.update(fdata)

        f.update(f['meta'])
        if 'Title' in f:
            f['title'] = f['Title']
        log.debug(f)

    # log.debug(files)

    template_response, meta = client.get_file_and_metadata(
        'templates/%s' % template)
    template_content = template_response.read()

    page_content = render_template(template_content, {
            'posts': files,
        })

    return page_content

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
    boxpub.run()
