from setuptools import setup, find_packages
# import codecs
# import os

# here = os.path.abspath(os.path.dirname(__file__))

# with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
#     long_description = "\n" + fh.read()

VERSION = '0.0.2'
DESCRIPTION = 'Topsis Package'
LONG_DESCRIPTION = 'A package as part of Predictive Analysis course.'

# Setting up
setup(
    name="Topsis-101903698",
    version=VERSION,
    author="Karanvir Singh",
    author_email="<ksingh5_be19@thapar.edu>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    setup_requires=['wheel'],
    install_requires=['numpy', 'pandas', 'tabulate'],
    keywords=['python', 'topsis', 'thapar'],
    classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9'
  ],
  entry_points={
        "console_scripts": [
            "topsis=topsis.topsis:getResults",
        ]
    },
)
