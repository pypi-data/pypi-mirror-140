from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='Topsis-Preetinder1-101903403',
  version='0.0.1',
  description='Topsis impelementation in python',
  long_description_content_type='text/markdown',
  long_description=open('README.txt').read(),
  url='',  
  author='Preetinder Kaur',
  author_email='dhillonpreeti2001@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='Topsis', 
  packages=find_packages(),
  install_requires=[''] 
)