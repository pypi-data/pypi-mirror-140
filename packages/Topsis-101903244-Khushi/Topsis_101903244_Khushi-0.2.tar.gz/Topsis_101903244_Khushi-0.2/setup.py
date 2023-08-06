from distutils.core import setup
setup(
  name = 'Topsis_101903244_Khushi',         
  packages = ['Topsis_101903244_Khushi'],  
  version = '0.2',
  license='MIT',
  description = 'Calculate Topsis score and save it in a csv file',
  author = 'Khushi Singhal',                   
  author_email = 'khushi.mitr03@gmail.com',     
  url = 'https://github.com/khushimitr/Topsis-Khushi-101903244',
  download_url = 'https://github.com/khushimitr/Topsis-Khushi-101903244/archive/refs/tags/v0.1.tar.gz',
  keywords = ['TOPSISSCORE', 'RANK', 'DATAFRAME'],
  install_requires=[
          'numpy',
          'pandas',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)