from setuptools import setup
 
setup(
  name = "pylibcheck",
  version = "0.0.1",
  description = "check if a pip module is installed",
  long_description = open("README.md").read(),
  long_description_content_type = "text/markdown",
  url = "https://github.com/rdimo/pylibcheck",
  project_urls={
    "Bug Tracker": "https://github.com/rdimo/pylibcheck/issues",
  },
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  author = "Rdimo",
  author_email = "contact.rdimo@gmail.com",
  license = "MIT", 
  keywords = "pylibcheck", 
  packages = ["pylibcheck"]
)