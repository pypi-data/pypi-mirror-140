from setuptools import setup
 
classifiers = [
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='Topsis-Chavvi-102097012',
  version='0.2.0',
  description = 'A python package to implement TOPSIS on a given dataset',
  #long_description=open('README.md').read(),
  url='',  
  author='Chavvi Bhatia',
  author_email='cbhatia_be19@thapar.edu',
  license='MIT', 
  classifiers=classifiers,
  keywords='TOPSIS', 
  packages=['Topsis_Chavvi'],
  #py_modules=['main'],
  #package_dir={'':'topsis'},
  install_requires=['pandas','numpy'],
  entry_points={"console_scripts":["topsis=Topsis_Chavvi.Topsis:main",]
                },
)
