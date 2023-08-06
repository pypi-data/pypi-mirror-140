from setuptools import setup
import pathlib
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()
setup(
  name = 'Topsis-Onkarjot-101903564',         # How you named your package folder (MyLib)
  packages = ['topsis'],   # Chose the same as "name"
  version = '0.3',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Topsis',   # Give a short description about your library
  author = 'Onkarjot Singh',                   # Type in your name
  author_email = 'osingh0066@gmail.com',      # Type in your E-Mail
  #url = 'https://github.com/onkarjotsingh',   # Provide either the link to your github or to your website
  #download_url = 'https://github.com/onkarjotsingh/onakrjot/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['SOME', 'MEANINGFULL', 'KEYWORDS'],   # Keywords that define your package best
  
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.9',
    #'Programming Language :: Python :: 2.9',
  ],
  
  include_package_data=True,
  install_requires=['pandas','numpy'],
  setup_requires=['wheel'],
  entry_points={
      "console_scripts": [
          "topsis=topsis.topsis:get_topsis_result",
        ]
    },
)

