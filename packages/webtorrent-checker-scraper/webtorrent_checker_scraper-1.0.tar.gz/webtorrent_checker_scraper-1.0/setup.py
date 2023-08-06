#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='webtorrent_checker_scraper',
      version='1.0',
      description='A simple script to scrape results of WebTorrent Checker (https://checker.openwebtorrent.com)',
      long_description_content_type='text/markdown; charset=UTF-8;',
      long_description=open('webtorrent_checker_scraper/README.md').read(),
      url='https://github.com/maaaaz/webtorrent-checker-scraper',
      author='Thomas D.',
      author_email='tdebize@mail.com',
      license='LGPL',
      classifiers=[
        'Topic :: Security',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python :: 3'
      ],
      keywords='webtorrent checker torrent magnet',
      packages=find_packages(),
      install_requires=['argparse', 'future', 'requests', 'lxml', 'beautifulsoup4', 'colorama', 'termcolor','torf'],
      python_requires='>=3',
      entry_points={
        'console_scripts': ['webtorrent_checker_scraper=webtorrent_checker_scraper.webtorrent_checker_scraper:main'],
      },
      include_package_data=True)