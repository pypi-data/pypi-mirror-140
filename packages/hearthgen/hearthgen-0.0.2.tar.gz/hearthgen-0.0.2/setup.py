import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = ["selenium>=4.1.1", "requests>=2.27.1"]

setuptools.setup(
    name="hearthgen",
    version="0.0.2",
    author='h4x4d',
    author_email='sidenkoleg@gmail.com',
    description='Library to make hearthstone cards in python!',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/h4x4d/hearthgen',
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'

)
