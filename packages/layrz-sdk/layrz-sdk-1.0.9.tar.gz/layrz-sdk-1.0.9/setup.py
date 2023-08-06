import setuptools

def read(filename):
  import os
  return open(os.path.join(os.path.dirname(__file__), filename)).read()

setuptools.setup(
  name="layrz-sdk",
  version="1.0.9",
  author="Layrz",
  author_email="software@layrz.com",
  url='https://gitlab.com/layrz-software/libraries/layrz-sdk',
  license='MIT',
  description="Layrz SDK",
  long_description=read('README.rst'),
  keywords='sdk goldenm lcl layrz compute language',
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  install_requires=[
    'requests',
    'pytz',
    'astroid'
  ],
  python_requires='>=3.8'
)
