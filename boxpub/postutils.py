import re
import markdown
import logging
import yaml
from yaml.scanner import ScannerError

log = logging.getLogger(__name__)

def split_markdown(md):
    """
    File content could have 0 or more yaml lines at the start
    """
    log.debug('split_markdown()')
    # log.debug(md)

    md = md.strip()

    meta_lines = []

    # line-oriented should work better
    # trim any lines with
    md = re.sub("[ \t]+\n", "\n", md)

    paras = re.split(
        '\n\n|\r\n\r\n|\r\r',
        md+'\n\n')  # whee, lots of linefeeds!

    # log.debug('paras:')
    # log.debug(paras)

    meta_string = paras[0]  # pretty sure it's going to have this either way
    # log.debug('meta_string:')
    # log.debug(meta_string)

    if meta_string:
        try:
            meta = yaml.load(meta_string)
            content = '\n\n'.join(paras[1:])
        except ScannerError, se:
            log.error(se.message)
            log.exception(se)
            meta = {}
        log.debug("STRIP META YAML: " + repr(meta))

    else:
        content = '\n\n'.join(paras)

    content = content.strip()

    # log.debug("split_markdown() returning: " + repr((meta, content)))
    return (meta, content)


def process_markdown(path, md):
    log.debug("process_markdown()")
    meta, content = split_markdown(md)
    # log.warning('meta, content')
    # log.debug(meta)

    html = markdown.markdown(content, ['extra', 'headerid', 'codehilite'])

    data = {
        'path': path,
        'meta': meta,
        'markdown': content,
        'html': html
    }

    # log.info(data)
    return data
