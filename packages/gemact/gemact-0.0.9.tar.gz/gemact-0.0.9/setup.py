from setuptools import setup

version = "0.0.9"
short_description="A comprehensive actuarial package for non-life (re)insurance."

def readme():
    with open('README.md') as f:
        README = f.read()
    return README

setup(name="gemact",
      version= version,
      description= short_description,
      long_description=readme(),
      long_description_content_type="text/markdown",
      url= "https://gem-analytics.github.io/gemact/",
      author="Gabriele Pittarello, Manfred Marvin Marchione, Edoardo Luini",
      author_email= "gabriele.pittarello@uniroma1.it",
      license="BSD 3-Clause",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python",
          "Operating System :: Unix",
          "Operating System :: MacOS :: MacOS X",
          "Operating System :: Microsoft :: Windows",
      ],
      py_modules=["__init__","distributions","gemdata","helperfunctions","lossaggregation","lossmodel","lossreserve","sobol"],
      packages=['gemact'],
      include_package_data=True,
      install_requires=["twiggy", "numpy>=1.21.4", "matplotlib>=3.5.0","scipy>=1.7.2"],
      project_urls = {
          'Source Code': 'https://github.com/GEM-analytics/gemact'
        }
      )