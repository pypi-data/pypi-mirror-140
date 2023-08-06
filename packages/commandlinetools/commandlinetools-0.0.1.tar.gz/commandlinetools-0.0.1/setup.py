from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='commandlinetools',
  version='0.0.1',
  description='Simplified commands and shortcuts for python Command Line tool',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='EmeraldRaidz',
  author_email='raidzemerald@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='command_line', 
  packages=find_packages(),
  install_requires=[''] 
)