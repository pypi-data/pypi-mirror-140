from setuptools import setup
setup(
  name = 'optix',         
  packages = ['optix'],   
  version = '0.2',      
  license='MIT',        
  description = 'Optics simplified',   
  author = 'David Tomecek',                  
  author_email = 'david.tomecek1@seznam.cz',     
  url = 'https://github.com/cavic19/optix',   
  download_url = 'https://github.com/cavic19/optix/archive/refs/tags/v_01.tar.gz',  
  keywords = ['optics', 'geometric optics', 'matrix optics'],   
  install_requires=[           
          'numpy>=1.19.4',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Science/Research',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3.9',
  ],
)
