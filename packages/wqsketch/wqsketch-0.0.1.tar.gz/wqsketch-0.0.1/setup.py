from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Weighted Quantile Sketch'

# Setting up
setup(
    name="wqsketch",
    version=VERSION,
    author="Benjamin Tay",
    author_email="<benjamin.tay85@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy'],
    keywords=['weighted', 'quantile', 'sketch', 'mergeable'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
