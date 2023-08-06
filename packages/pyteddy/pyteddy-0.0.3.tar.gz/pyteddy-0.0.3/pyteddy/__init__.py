from . import templates

def get_template(name='_default_package_template'):
    return getattr(templates, '_' + name)
