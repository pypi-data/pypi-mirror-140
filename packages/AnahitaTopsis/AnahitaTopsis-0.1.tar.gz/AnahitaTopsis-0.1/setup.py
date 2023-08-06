from distutils.core import setup

setup(name='AnahitaTopsis',
      packages = ['AnahitaTopsis'],
      version='0.1',
      description='Topsis Package',
      url='https://github.com/singhania0601/AnahitaTopsis',
      download_url = 'https://github.com/singhania0601/AnahitaTopsis/archive/refs/tags/v_01.tar.gz', #FILL IN LATER
      author='Anahita',
      author_email='asinghania2_be19@thapar.edu',
      keywords = ['topsis', 'ranking'],
      license='MIT', #YOUR LICENSE HERE!

      install_requires=['pandas','numpy','topsispy'],  #YOUR DEPENDENCIES HERE
  

      classifiers=[
        'Development Status :: 3 - Alpha',      # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
        'Intended Audience :: Developers',      
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License', # Your License Here  
        'Programming Language :: Python :: 3',    # List Python versions that you support Here  
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        ],
)
