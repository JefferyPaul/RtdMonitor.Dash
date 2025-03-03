# cache_config.py
from flask_caching import Cache


def configure_cache(app):
    cache = Cache(app.server, config={
        'CACHE_TYPE': 'simple'
    })
    return cache
