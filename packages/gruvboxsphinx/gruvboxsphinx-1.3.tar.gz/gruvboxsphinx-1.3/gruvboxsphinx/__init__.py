import os
from datetime import datetime

__version__ = '1.3'
__version_full__ = __version__


def get_path():
    """Shortcut for users whose theme is next to their conf.py."""
    # Theme directory is defined as our parent directory
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def update_context(app, pagename, templatename, context, doctree):
    context['insegel_version'] = __version_full__


def setup(app):
    if hasattr(app, 'add_html_theme'):
        theme_path = os.path.abspath(os.path.dirname(__file__))
        app.add_html_theme('gruvboxsphinx', theme_path)
    app.connect('html-page-context', update_context)
