import setuptools

def read(filename):
  import os
  return open(os.path.join(os.path.dirname(__file__), filename)).read()

setuptools.setup(
  name="layrz-simulator",
  version="1.0.0",
  author="Layrz",
  author_email="software@layrz.com",
  url='https://gitlab.com/layrz-software/libraries/sdk-simulator',
  license='MIT',
  description="Layrz Simulator",
  long_description=read('README.rst'),
  keywords='sdk goldenm lcl layrz compute language simulator',
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  install_requires=[
    'requests',
    'pytz',
    'matplotlib',
    'layrz-sdk>=1.0.0'
  ],
  python_requires='>=3.8'
)
