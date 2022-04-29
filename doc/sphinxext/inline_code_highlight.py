from docutils.parsers.rst.roles import code_role


def python_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    options = {'language': 'python'}
    return code_role(
        role,
        rawtext,
        text,
        lineno,
        inliner,
        options=options,
        content=content
    )


def setup(app):
    app.add_role('python', python_role)
    app.add_role('py', python_role)
