from setuptools import setup

with open("README.md", "r") as fh:
  long_description = fh.read()

setup(
  name = "packagenamedisplay",
  version = "1.0.0",
  description = "Module description.",
  long_description = long_description,
  long_description_content_type = "text/markdown",
  url = "https://www.discordapp.com/users/771212911606628363",
  author = "Author's name",
  author_email = "devpsingh2020@gmail.com",
  license = "GNU General Public License v3 (GPLv3)",
  packages=["module_name"],
  classifiers = [
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
  "Operating System :: OS Independent",
],
  zip_safe=True,
  python_requires = ">=3.0",
)