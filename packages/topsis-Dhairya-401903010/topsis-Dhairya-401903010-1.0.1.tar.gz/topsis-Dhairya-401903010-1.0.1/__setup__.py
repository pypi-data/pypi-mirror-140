import setuptools

with open("README.txt", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="topsis-Dhairya-401903010",
    version="1.0.1",
    author="Dhairya Mahajan",
    author_email="dhairyamahajan07@gmail.com",
    description="Decision Making using topsis (Python Package)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[            
          'pandas',
          'numpy'
      ],
    classifiers=[
      'License :: OSI Approved :: MIT License', 
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.7'
    ],
    )