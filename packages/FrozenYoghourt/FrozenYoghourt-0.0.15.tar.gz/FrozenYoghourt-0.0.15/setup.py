from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

# long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.md').read()
setup(
  name='FrozenYoghourt',
  version='0.0.15',
  description='Numerical and Symbolic Manipulation for Quantum Computing',
  url='https://pypi.org/project/FrozenYoghourt/',  
  author='Peter Montgomery',
  author_email='petermontgomery056@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='quantum computing', 
  packages=find_packages(),
  install_requires=[''] 
)