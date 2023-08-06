import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='Topsis-Nanaki-101903195',  
    version='0.1.1',
    author="Nanaki",
    license='MIT',
    author_email="nanakidhanoa@gmail.com",
    description="Multi Criteria Decision Making using TOPSIS (Python Package)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url = 'https://github.com/nanaki-dhanoa/Topsis.git',
    download_url = 'https://github.com/nanaki-dhanoa/Topsis/archive/refs/tags/v_0.01.zip',
    packages=setuptools.find_packages(),
    install_requires=[            
          'pandas',
          'numpy'
      ],
    classifiers=[
      'License :: OSI Approved :: MIT License', 
      'Programming Language :: Python :: 3.9',
    ],
 )
