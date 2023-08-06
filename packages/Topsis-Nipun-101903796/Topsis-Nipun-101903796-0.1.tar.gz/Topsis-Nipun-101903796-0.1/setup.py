"""

@author: Nipun Verma

"""
from distutils.core import setup
setup(
  name = 'Topsis-Nipun-101903796',         # How you named your package folder
  packages = ['Topsis-Nipun-101903796'],   # Chose the same as "name"
  version = '0.1',      
  license='MIT',        
  description = 'Topsis package python',   
  author = 'Nipun Verma',                   
  author_email = 'nipunverma39@gmail.com',     
  url = 'https://github.com/Nipun3120/Topsis-Nipun-Verma-101903796.git',   
  download_url='https://github.com/Nipun3120/Topsis-Nipun-Verma-101903796/archive/refs/tags/0.1.tar.gz',
  Keywords = ['Python', 'Topsis', '101903796'],   # Keywords for package
  install_requires = [          # dependencies required for package to work
          'numpy',
          'pandas',
      ],
      
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
