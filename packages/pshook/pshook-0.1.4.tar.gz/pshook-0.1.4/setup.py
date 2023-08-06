import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pshook",
    version="0.1.4",
    author="Jakob Simon-Gaarde",
    author_email="jakobsg@simon-gaarde.dk",
    description="A small tool that enables monitoring of executable files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/jakobsg/pshook",
    packages=setuptools.find_packages(),
    scripts=['scripts/pshook'],
    install_requires = [
        'psutil==5.6.3'
    ],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.6',
)
