AUTHOR = 'Srini Kadamati'
SITENAME = 'Srini Kadamati'

PATH = 'content'

TIMEZONE = 'America/New_York'
COPYRIGHT_START_YEAR = 2021
DEFAULT_LANG = 'en'
LOGO_IMAGE = '/images/logo.jpg'
FAVICON_IMAGE = '/images/favicon.ico'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = "feeds/all.atom.xml"
CATEGORY_FEED_ATOM = "feeds/category/%s.atom.xml"
TAG_FEED_ATOM = "feeds/tag/%s.atom.xml"

# Blogroll
NAV_LINKS = [
    {'name': 'Home', 'url': '/'},
    {'name': 'Blog', 'url': '/blog/'},
    {'name': 'About', 'url': '/about/'},
    {'name': 'RSS', 'url': '/feeds/all.atom.xml'}
]

LINKS = (('Pelican', 'https://getpelican.com/'),
         ('Python.org', 'https://www.python.org/'),
         ('Jinja2', 'https://palletsprojects.com/p/jinja/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = False

PAGE_PATHS = ['pages']
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'

SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'monthly',
        'pages': 'monthly'
    }
}

STATIC_PATHS = ['images', 'extra/CNAME']
EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'},'extra/robots.txt': {'path': 'robots.txt'}}

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

GOOGLE_ANALYTICS = 'UA-215861180-1'
DOMAIN = "viz.gl"

CACHE_CONTENT = False
AUTORELOAD_IGNORE_CACHE = True

# Custom stuff by Srini
THEME = "newbird"
