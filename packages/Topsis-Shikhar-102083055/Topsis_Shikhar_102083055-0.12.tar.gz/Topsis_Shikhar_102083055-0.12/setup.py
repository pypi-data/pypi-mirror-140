from distutils.core import setup
setup(
  name = 'Topsis_Shikhar_102083055',         
  packages = ['Topsis_Shikhar_102083055'],   
  version = '0.12',     
  license='MIT',       
  description = 'Topsis Calculation',   
  author = 'Shikhar Saini',                  
  author_email = 'shikharsaini25@gmail.com', 
  url = 'https://github.com/shikharsaini',   
  keywords = ['Topsis', 'TopsisPackage'],   
  install_requires=[     
           'numpy',
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