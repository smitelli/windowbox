import re
from setuptools import find_namespace_packages, setup

with open('windowbox/__init__.py', 'r') as fh:
    version = re.search(r"__version__ = '(.*?)'", fh.read()).group(1)

with open('README.md', 'r') as fh:
    readme = fh.read()

setup(
    name='windowbox',
    version=version,
    author='Scott Smitelli',
    author_email='scott@smitelli.com',
    description="Don't call it a moblog / I've posted for years.",
    long_description=readme,
    packages=find_namespace_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=[
        'Flask-Assets==0.12',
        'Flask-SQLAlchemy==2.5.1',
        'Flask==1.1.4',
        'htmlmin==0.1.12',
        'libsass==0.19.4',
        'lxml==4.6.5',
        'Pillow==8.3.2',
        'requests==2.22.0',
        'tweepy==3.8.0',
    ],
    extras_require={
        'dev': [
            'flake8==3.7.9',
            'pytest-cov==2.8.1',
            'pytest==5.2.2',
            'python-dotenv==0.10.3'
        ]
    },
    entry_points={
        'console_scripts': [
            'windowbox-bark = windowbox.bark:main',
            'windowbox-fetch = windowbox.fetch:main'
        ]
    },
)
