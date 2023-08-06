from setuptools import setup, find_packages

classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Knowledge',      
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ]

setup(
  name = 'Vehicles',          
  version = '0.0.1',     
  license='MIT',        
  description = 'It is a base on Vehicles type and its module.',   
  author = 'Prachi shah',                  
  author_email = 'prachivshah03@gmail.com',      
  url = 'https://github.com/PrachiiiShah', 
  keywords = 'vehicletype',   
  packages=find_packages(), 
  install_requires=['']
)