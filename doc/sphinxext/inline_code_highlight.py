from docutils.core import Publisher
from docutils.parsers.rst.roles import code_role


# Monkey patch docutils to give short css names
# credit: http://stackoverflow.com/a/21766874/832573
def process_programmatic_settings(self, settings_spec,
                                  settings_overrides,
                                  config_section):
    if self.settings is None:
        defaults = (settings_overrides or {}).copy()
        defaults.setdefault('traceback', True)
        defaults.setdefault('syntax_highlight', 'short')
        self.get_settings(settings_spec=settings_spec,
                          config_section=config_section,
                          **defaults)

Publisher.process_programmatic_settings = process_programmatic_settings


def python_role(role, rawtext, text, lineno,
                inliner, options={}, content=[]):
    options = {'language': 'python'}
    return code_role(role, rawtext, text, lineno,
                     inliner, options=options, content=content)


def setup(app):
    app.add_role('python', python_role)
    app.add_role('py', python_role)
