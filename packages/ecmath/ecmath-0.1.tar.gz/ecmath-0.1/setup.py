from distutils.core import setup

setup(
  name = 'ecmath',
  packages = ['ecmath'],
  version = '0.1',
  license='MIT',
  description = 'Basic elliptic curve arithmetic',
  author = 'Johan Kirsten',
  author_email = 'kirsten.johanf@gmail.com',
  url = 'https://github.com/johankirsten/ecmath',
  download_url = 'https://github.com/johankirsten/ecmath/archive/refs/tags/v_02.tar.gz',
  keywords = ['Elliptic curve'],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.9',
  ],
)