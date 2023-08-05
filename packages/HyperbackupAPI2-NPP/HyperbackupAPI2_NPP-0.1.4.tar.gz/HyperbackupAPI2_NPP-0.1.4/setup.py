import re
from setuptools import setup


versio = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('HyperBackupAPI2\HyperbackupAPI2_NPP.py').read(),
    re.M
    ).group(1)


with open("readme.md", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(name='HyperbackupAPI2_NPP',
      version=versio,
      description='API Basica per a synologys Hyperbackup',
      long_description=long_descr,
      long_description_content_type='text/markdown',
      url='https://github.com/NilPujolPorta/HyperbackupAPI2',
      author='Nil Pujol Porta',
      author_email='nilpujolporta@gmail.com',
      license='GNU',
      packages=['HyperbackupAPI2'],
      install_requires=[
          'argparse',
          "setuptools>=42",
          "wheel",
          "pyyaml",
          "requests",
          "mysql-connector-python",
          "selenium"
      ],
	entry_points = {
        "console_scripts": ['HyperBackupAPI2-NPP = HyperBackupAPI2.HyperbackupAPI2_NPP:main']
        },
      zip_safe=False)
