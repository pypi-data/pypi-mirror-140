from django.conf.urls import RegexURLPattern, RegexURLResolver
from django.core import urlresolvers
urls = urlresolvers.get_resolver()

def if_none(value):
    if value:
        return value
    return ''

def print_urls(urls, parent_pattern=None):
    for url in urls.url_patterns:
        if isinstance(url, RegexURLResolver):
            print_urls(url, if_none(parent_pattern) + url.regex.pattern)
        elif isinstance(url, RegexURLPattern):
            print(if_none(parent_pattern) + url.regex.pattern)

print_urls(urls)