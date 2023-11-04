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
        'Flask-Assets==2.1.0',
        'Flask-SQLAlchemy==3.0.3',
        'Flask==2.3.3',
        'MarkupSafe==2.1.2',
        'Pillow==10.0.1',
        'htmlmin==0.1.12',
        'libsass==0.22.0',
        'lxml==4.9.2',
        'requests==2.31.0',
        'tweepy==3.10.0'
    ],
    extras_require={
        'dev': [
            'flake8==6.0.0',
            'pytest-cov==4.0.0',
            'pytest==7.3.1',
            'python-dotenv==1.0.0'
        ]
    },
    entry_points={
        'console_scripts': [
            'windowbox-bark = windowbox.bark:main',
            'windowbox-fetch = windowbox.fetch:main'
        ]
    },
)
