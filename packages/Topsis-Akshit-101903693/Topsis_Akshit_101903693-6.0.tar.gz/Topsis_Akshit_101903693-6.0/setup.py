from setuptools import setup, find_packages

def readme():
    with open('README.txt') as f:
        README = f.read()
    return README  

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='Topsis_Akshit_101903693',
  version='6.0',
  description='Implements TOPSIS',
  long_description= 'INSTRUCTION MANUAL: \n Some important points to keep in mind while using the package: \n Enter Correct number of parameters (inputFileName, Weights, Impacts, resultFileName) to execute the program \nMake sure you enter correct name of the file otherwise you will encounter a “File not Found” exception \n The input file must contain three or more columns \n 2nd to last columns, they must contain numeric values only \n Number of weights, number of impacts and number of columns (from 2nd to last columns) must be same. \n The values of Impacts must be either +ve or -ve \n Values of Impacts and weights must be separated by ‘,’ (comma).',         
  long_description_content_type="text/plain",
  url='https://github.com/akshit23401/TOPSIS-Implementation-in-Python/',  
  author='Akshit Bansal',
  author_email='abansal2_be19@thapar.edu',
  license='MIT', 
  classifiers=classifiers,
  keywords='', 
  packages=find_packages(),
  install_requires=[''] 
)

##+ '\n\n' + open('CHANGELOG.txt').read()