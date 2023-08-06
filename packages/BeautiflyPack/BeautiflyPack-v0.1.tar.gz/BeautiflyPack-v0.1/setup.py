from distutils.core import setup
setup(
  name = 'BeautiflyPack',         # How you named your package folder (MyLib)
  packages = ['BeautiflyPack'],   # Chose the same as "name"
  version = 'v0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Group E 1st Python Package available to the whole world',   # Give a short description about your library
  author = 'Group E',                   # Type in your name
  author_email = 'matter.alotaibi@student.ie.edu',      # Type in your E-Mail
  url = 'https://github.com/IE2020Term3GroupE/Beautifly',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/IE2020Term3GroupE/Beautifly/archive/refs/tags/v0.1.tar.gz',    # I explain this later on
  keywords = ['Package', 'Hello World'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          
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