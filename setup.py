from setuptools import setup, find_packages
setup(
    name = "WTForm",
    version = "1.0",
    packages = ['wtform'],
    package_dir = {'wtform': 'wtform'},
    author = "Christian Joergensen",
    author_email = "christian.joergensen@gmta.info",
    description = "WTForm is an extension to the django newforms library.",
    long_description = "WTForm is an extension to the django newforms library allowing the developer, in a very flexible way, to layout the form fields using fieldsets and columns",
    license = "http://creativecommons.org/licenses/by-sa/3.0/",
    keywords = "django newforms forms yui",
    classifiers = ['Development Status :: 5 - Production/Stable',
                   'License :: Freely Distributable',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
                   'Topic :: Software Development :: Libraries :: Python Modules']
)
