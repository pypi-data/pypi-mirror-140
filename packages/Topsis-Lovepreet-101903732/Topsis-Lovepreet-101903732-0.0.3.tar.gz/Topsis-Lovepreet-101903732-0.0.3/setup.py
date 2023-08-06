from setuptools import setup, find_packages


VERSION = '0.0.3'
DESCRIPTION = 'Implement TOPSIS on a dataset through command line'
LONG_DESCRIPTION = 'A package that allows to implement TOPSIS. Following query on terminal will provide you the best and worst decisions for the dataset. python topsis.py input.csv 1,1,1,2,1 +,+,-,+,+ output-file.csv'


# Setting up
setup(
    name="Topsis-Lovepreet-101903732",
    version='0.0.3',
    author="Lovepreet Singh",
    author_email="lovithindcoc@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=['topsis'],
    install_requires=["pandas","numpy"],
    keywords=['python', 'topsis'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)