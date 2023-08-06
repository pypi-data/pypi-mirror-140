from distutils.core import setup
setup(
  name = 'Topsis-Garvit-101903778',         
  packages = ['Topsis-Garvit-101903778'],  
  version = '0.1',      
  license='MIT',        
  description = 'A Python package to find TOPSIS for multi-criteria decision analysis method',   
  author_email = 'nagiagarvit@live.com',      
  url = 'https://github.com/Garvit-25/Topsis-Garvit-101903778',   
  download_url = 'https://github.com/Garvit-25/Topsis-Garvit-101903778/archive/refs/tags/0.1.tar.gz',    
  keywords = ['TOPSIS','TIET'],   
  install_requires=[            
          'pandas',
          'tabulate',
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