import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='Discohook',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='A basic Library to send Discord Webhook',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/Janakthegamer/Discohook',
    project_urls={
        "Bug Tracker": "https://github.com/Janakthegamer/Discohook/issues",
    },
    install_requires=[
        'requests>=2.19.1',
    ],
    author='JanakXD',
    author_email='janak@panarastudios.in',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    entry_points={
        'console_scripts': [
            'discohook=discohook.__main__:main',
        ],
    },
)
