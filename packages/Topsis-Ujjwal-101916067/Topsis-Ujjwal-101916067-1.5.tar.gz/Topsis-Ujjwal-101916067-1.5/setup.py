# from setuptools import setup, find_packages
# setup(
#   name = 'Ujjwal_TOPSIS',         # How you named your package folder (MyLib)
#   packages = ['Ujjwal_TOPSIS'],   # Chose the same as "name"
#   version = '0.1',      # Start with a small number and increase it with every change you make
#   license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
#   description = 'This is the package which is helpful to compare different models based on their weights and their impacts on the basis of TOPSIS.',   # Give a short description about your library
#   author = 'Ujjwal Madaan',                   # Type in your name
#   author_email = 'madaan.ujjwal05@gmail.com',      # Type in your E-Mail
#   url = 'https://github.com/Ujjwal-Madaan/Ujjwal_TOPSIS',   # Provide either the link to your github or to your website
#   download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
#   keywords = ['ML', 'Models', 'Compare', 'Performance'],   # Keywords that define your package best
#   install_requires=[            # I get to this in a second
#           'pandas',
#           'numpy',
#           'copy',
#           'sys',
#           'os',
#           'logging'
#       ],
#   classifiers=[
#     'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
#     'Intended Audience :: Developers',      # Define that your audience are developers
#     'Topic :: Software Development :: Build Tools',
#     'License :: OSI Approved :: MIT License',   # Again, pick a license 
#     'Programming Language :: Python :: 3.6',   #Specify which pyhton versions that you want to support
#     'Programming Language :: Python :: 3.8',
#     'Programming Language :: Python :: 3.9',
#   ],
# )


from setuptools import setup, find_packages
# import codecs
# import os


DESCRIPTION = 'Comparing the models based on TOPSIS'
LONG_DESCRIPTION = 'It takes csv file with the model information, weights, impacts as input and returns the ranking of the model based on the certain algorithm.'

# Setting up
setup(
    name="Topsis-Ujjwal-101916067",
    version='1.5',
    author="Ujjwal Madaan",
    author_email="madaan.ujjwal05@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[            # I get to this in a second
          'pandas',
          'numpy',
      ],
    keywords=['ML', 'Models', 'Compare', 'Performance'],
    classifiers=[
      'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
      'Intended Audience :: Developers',      # Define that your audience are developers
      'Topic :: Software Development :: Build Tools',
      'License :: OSI Approved :: MIT License',   # Again, pick a license 
      'Programming Language :: Python :: 3.6',   #Specify which pyhton versions that you want to support
      'Programming Language :: Python :: 3.8',
      'Programming Language :: Python :: 3.9',
    ],
)