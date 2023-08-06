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
  version='5.0',
  description='Implements TOPSIS',
  long_description= 'Some important points to keep in mind while using the package: \n Enter Correct number of parameters (inputFileName, Weights, Impacts, resultFileName) to execute the program ',         
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