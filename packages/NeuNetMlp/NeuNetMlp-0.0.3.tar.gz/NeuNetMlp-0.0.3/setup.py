from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='NeuNetMlp',
  version='0.0.3',
  description='A Multilayered Perceptron Nueral Network Implemented In Python & Numpy',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Pranav Sai',
  author_email='pranavs31899@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='Neural Network, Multi-Layered Perceptron', 
  packages=find_packages(),
  install_requires=['numpy'] 
)