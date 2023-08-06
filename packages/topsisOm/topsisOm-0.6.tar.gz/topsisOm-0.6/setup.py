from distutils.core import setup
setup(
  name = 'topsisOm',         
  packages = ['topsisOm'],   
  version = '0.6',      
  license='MIT',       
  description = 'This package helps to get the topsis score from the given dataframe',   # Give a short description about your library
  author = 'Om Gupta',                   # Type in your name
  author_email = 'omstringtheory@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/om-guptaa',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/om-guptaa/topsisOm/archive/refs/tags/v_06.tar.gz',    # I explain this later on
  keywords = ['Topsis', 'Ranking'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pandas',
          'numpy',
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
