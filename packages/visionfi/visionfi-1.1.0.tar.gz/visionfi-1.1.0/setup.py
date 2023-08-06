from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='visionfi',
  version='1.1.0',
  description='An library for visualization and outlier handling',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Visiofi_Team',
  author_email='',
  license='MIT', 
  classifiers=classifiers,
  keywords='visualization', 
  packages=find_packages(),
  install_requires=[''] 
)
