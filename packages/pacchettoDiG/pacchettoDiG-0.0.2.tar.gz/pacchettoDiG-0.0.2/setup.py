from setuptools import setup

version = "0.0.2"
short_description="A comprehensive useless package."

def readme():
    with open('README.md') as f:
        README = f.read()
    return README

setup(name="pacchettoDiG",
      version=version,
      description= short_description,
      long_description=readme(),
      long_description_content_type="text/markdown",
      author="Gabriele Pittarello",
      license="BSD 3-Clause",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python",
          "Operating System :: Unix",
          "Operating System :: MacOS :: MacOS X",
          "Operating System :: Microsoft :: Windows",
      ],
      py_modules=["module1","module2","__init__"],
      packages=["pckg"],
      include_package_data=True,
      install_requires=["twiggy", "numpy>=1.21.4", "matplotlib>=3.5.0","scipy>=1.7.2"],
      project_urls={
          'Source Code': 'https://github.com/GEM-analytics'
      }
      )