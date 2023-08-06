import setuptools

setuptools.setup(
    name="tsuyo-hello",                       # This is the name of the package
    version="1.0.0",                          # The initial release version
    description="Hello from Python",
    packages=setuptools.find_packages('src'), # List of all python modules to be installed
    python_requires='>=3.6',                  # Minimum version requirement of the package
    package_dir={'':'src'},                   # Directory of the source code of the package
    install_requires=[]                       # Install other dependencies if any
)
