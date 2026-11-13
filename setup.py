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
    python_requires='>=3.9',
    install_requires=[
        'Flask-Assets==2.1.0',
        'Flask-SQLAlchemy==3.1.1',
        'Flask==3.1.3',
        'MarkupSafe==3.0.4',
        'Pillow==11.3.0',
        'htmlmin==0.1.12',
        'libsass==0.23.0',
        'lxml==6.1.3',
        'requests==2.32.5'
    ],
    extras_require={
        'dev': [
            'flake8==7.3.0',
            'pytest-cov==7.1.0',
            'pytest==8.4.2',
            'python-dotenv==1.2.1'
        ]
    },
    entry_points={
        'console_scripts': [
            'windowbox-fetch = windowbox.fetch:main'
        ]
    },
)
