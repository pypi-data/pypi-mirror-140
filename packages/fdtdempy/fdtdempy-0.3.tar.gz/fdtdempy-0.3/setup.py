from distutils.core import setup
from distutils.core import Extension
from Cython.Build import cythonize

sourcefiles = ['fdtdempy/*.pyx']

extensions = [Extension("*", sourcefiles)]

setup(
  name = 'fdtdempy',
  ext_modules=cythonize(extensions, language_level = "3"),
  packages = ['fdtdempy'],
  version = '0.3',
  license='MIT',
  description = 'FDTD Electromagnetic Field Simulation',
  author = 'Johan Kirsten',
  author_email = 'kirsten.johanf@gmail.com',
  url = 'https://github.com/johankirsten/fdtdempy',
  download_url = 'https://github.com/johankirsten/fdtdempy/archive/refs/tags/v_03.tar.gz',
  keywords = ['FDTD', 'Electromagnetism', 'Simulation'],
  setup_requires=["cython"],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.9',
  ],
)