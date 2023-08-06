from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Package for inferring latent calcium activity from two-channel imaging'

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="calcium_inference",
    version=VERSION,
    author="Matthew S. Creamer",
    author_email="matthew.s.creamer@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['torch',
                      'numpy',
                      'scipy',
                      'matplotlib',
                      ],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'calcium', 'inference', 'two-channel', 'imaging'],
    classifiers=[
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
    ]
)