import logging
import config
from datetime import datetime
import jinja2
import markdown

import dropbox
from dropbox import client, session
# from dropbox.rest import ErrorResponse

from flask import Flask, request

from postutils import split_markdown, process_markdown

logging.basicConfig(level=logging.DEBUG)
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


@boxpub.route('/page/<page>')
def blog_page_handle(page, template='post.html'):
    log.debug('blog_page_handle()')

    target_file = "/pages/%s.md" % (page)

    page_content = render_file_with_template(target_file, template)

    return page_content


@boxpub.route('/posts/<year>/<month>/<day>/<filename>')
def blog_post_handle(year, month, day, filename, template='post.html'):
    log.debug('blog_post_handle()')
    log.info('Dropbox post request')

    target_file = "/posts/%s-%s-%s-%s.md" % (year, month, day, filename)

    page_content = render_file_with_template(target_file, template)

    return page_content


if __name__ == "__main__":
    boxpub.run()