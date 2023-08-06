from distutils.core import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
  name = 'Topsis_Abhinav_101903756',         
  packages = ['Topsis_Abhinav_101903756'],   
  version = '3.0',     
  license='MIT',       
  description = 'Topsis Calculation',   
  long_description=long_description,
  long_description_content_type="text/markdown",
  author = 'Abhinav Sinha',                  
  author_email = 'sinha18abhinav@gmail.com',  
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
