from distutils.core import setup
setup(
  name = 'TOPSIS-Tushar-101903407',         # How you named your package folder (MyLib)
  packages = ['TOPSIS-Tushar-101903407'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Topsis Value Calculator CalcTopsis is a Python package implementing Topsis method sed for multi-criteria decision analysis. Topsis stands for Technique for Order of Preference by Similarity to Ideal Solution Just provide your input attributes and it will give you the results', 
  author = 'Tushar Chugh',                   # Type in your name
  author_email = 'tchugh_be19@thapar.edu',      # Type in your E-Mail
  url = 'https://github.com/user/Topsis-Tushar-101903407',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/TusharChugh2212/Topsis-Tushar-101903407/archive/refs/tags/v_02.tar.gz',    # I explain this later on
  keywords = ['SOME', 'MEANINGFULL', 'KEYWORDS'],   # Keywords that define your package best
  install_requires=[
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
