from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='RugbyPython',
  version='0.0.4',
  description='A package for rugby analytics.',
  long_description='A package for rugby analytics that makes it easy to plot custom pitches with matplotlib.',
  url='',  
  author='Maverick Guest',
  author_email='maverickguest@outlook.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='sport', 
  packages=find_packages(),
  install_requires=['Matplotlib'] 
)
