from setuptools import setup, find_packages 

with open("README.md", "r") as readme_file:
    readme = readme_file.read()
    
requirements = ["ipython>=6", "numpy", "sympy", "scipy>=1.0"]

description = ("Reduce monomial basis for SDP computations for ROM of Rayleigh–Bénard convection.")

setup(
      name="ReduceMonomsRBC",
      version="0.2",
      author="Matt Olson",
      author_email="mlolson@umich.edu",
      description=description,
      long_description=readme,
      long_description_content_type="text/markdown",
      url="https://github.com/PeriodicROM/ReduceMonomsRBC/",
      packages=["ReduceMonomsRBC"],
      install_requires=requirements,
      classifiers=[
          "Programming Language :: Python :: 3.7",
          "License :: OSI Approved :: MIT License",
      ],
) 