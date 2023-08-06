import pathlib
from distutils.core import setup
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
  name = 'Topsis-Esha-101917137',         # How you named your package folder (MyLib)
  packages = ['Topsis-Esha-101917137'],   # Chose the same as "name"
  version = '1.0.1',      # Start with a small number and increase it with every change you make
  license = 'MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'TOPSIS method for Multiple-Criteria Decision Making (MCDM).',   # Give a short description about your library
  long_description = README,
  long_description_content_type = "text/markdown",   # Give a short description about your library
  author = 'Esha Sherring',                   # Type in your name
  author_email = 'esherring2016@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/Esha-Sherring/Topsis-Esha-101917137.git',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/Esha-Sherring/Topsis-Esha-101917137/archive/1.0.1.tar.gz',    # I explain this later on
  keywords = ['TOPSIS'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pandas',
          'numpy'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.6',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.7'
  ]
)