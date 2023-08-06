# -*- coding: utf-8 -*-
"""
Created on Sun Feb 27 16:42:04 2022

@author: jayan
"""

from distutils.core import setup
setup(
  name = 'Topsis-Jayant-101903643',         # How you named your package folder (MyLib)
  packages = ['Topsis-Jayant-101903643'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Topsis package python',   # Give a short description about your library
  author = 'Jayant Sharma',                   # Type in your name
  author_email = 'jsharma1_be19@thapar.edu',      # Type in your E-Mail
  url = 'https://github.com/JayantSharma777/101903643-topsis',   # Provide either the link to your github or to your website
  download_url='https://github.com/JayantSharma777/Topsis-Jayant-101903643/archive/refs/tags/v_0.1.tar.gz',
  Keywords = ['Python', 'Topsis', '101903643'],   # Keywords that define your package best
          
  install_requires = [            # I get to this in a second
          'numpy',
          'pandas',
      ],
      
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)