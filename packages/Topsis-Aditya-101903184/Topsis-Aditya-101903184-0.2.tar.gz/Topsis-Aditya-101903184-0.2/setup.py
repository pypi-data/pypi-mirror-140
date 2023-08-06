from distutils.core import setup
setup(
  name = 'Topsis-Aditya-101903184',         # How you named your package folder (MyLib)
  packages = ['Topsis-Aditya-101903184'],   # Chose the same as "name"
  version = '0.2',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'A Topsis library to work in an instant and rank the given records',   # Give a short description about your library
  author = 'Aditya Gupta',                   # Type in your name
  author_email = 'agupta6_be19@thapar.edu',      # Type in your E-Mail
  url = 'https://github.com/mostlyAditya/Topsis',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/mostlyAditya/Topsis/archive/v_02.tar.gz',    # I explain this later on
  keywords = ['Python', 'Topsis'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'validators',
          'beautifulsoup4',
          'numpy',
          'pandas'
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