import pyteddy.templates


def get_template(name='_default_package_template'):
    return getattr(pyteddy.templates, '_' + name)
