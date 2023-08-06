from distutils.core import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
  name = 'Topsis_Armaan_101903292',         
  packages = ['Topsis_Armaan_101903292'],   
  version = '2.00',     
  license='MIT',       
  description = 'Topsis Calculation',   
  long_description=long_description,
  long_description_content_type="text/markdown",
  author = 'Armaan Bhardwaj',                  
  author_email = 'armaanbhardwaj23@gmail.com', 
  url = 'https://github.com/armaanbhardwaj23',   
  keywords = ['Topsis', 'TopsisPackage'],   
  install_requires=[     
          'pandas',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',     
    'Intended Audience :: Developers',     
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
