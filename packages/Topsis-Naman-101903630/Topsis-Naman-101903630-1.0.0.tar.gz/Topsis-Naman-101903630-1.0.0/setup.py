from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: OS Independent',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='Topsis-Naman-101903630',
  version='1.0.0',
  description='Topsis Calculator',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Naman Garg',
  author_email='ngarg2_be19@thapar.edu',
  license='MIT', 
  classifiers=classifiers,
  keywords='Topsis-Naman-101903630', 
  packages=find_packages(),
  install_requires=['Topsis-Naman-101903630','numpy','pandas'] 
)