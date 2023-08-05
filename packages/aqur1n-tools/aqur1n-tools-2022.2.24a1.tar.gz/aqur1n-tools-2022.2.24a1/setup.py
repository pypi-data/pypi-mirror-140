from setuptools import setup
import atools

readme = ""
with open("README.md", "r", encoding="utf-8") as file:
    readme = file.read()

setup(name='aqur1n-tools',
      author=atools.__author__,
      version=atools.__version__,
      license='MIT',
      long_description=readme,
      long_description_content_type="text/markdown",
      description='Collection of modules for convenient work.',
      packages=['atools'],
      url=atools.__github__,
      project_urls={
        "Bug Tracker": "https://github.com/aqur1n-lab/aqur1n-tools/issues",
        "Wiki": "https://github.com/aqur1n-lab/aqur1n-tools/wiki",
      },
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
      ],
      python_requires=">=3.5",
      zip_safe=False)
      