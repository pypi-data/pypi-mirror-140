from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()
setup(
    name='foldrm',
    version='0.0.2',
    packages=find_packages(),
    url='https://github.com/hwd404/FOLD-RM',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    author='hwd404',
    author_email='hwd404@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown"
)
