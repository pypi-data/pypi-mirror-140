from distutils.core import setup
setup(
  name = 'Topsis-Parth-101903297',
  packages = ['Topsis-Parth-101903297'],
  version = '0.1',
  license='MIT',
  description = 'Calculate Topsis score and save it in a csv file',
  author = 'Parth Mehta',
  author_email = 'mehtaparth030@gmail.com',
  url = 'https://github.com/parthmehtaa21/Topsis-Parth-101903297',
  download_url = 'https://github.com/parthmehtaa21/Topsis-Parth-101903297/archive/refs/tags/v_01.tar.gz',
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