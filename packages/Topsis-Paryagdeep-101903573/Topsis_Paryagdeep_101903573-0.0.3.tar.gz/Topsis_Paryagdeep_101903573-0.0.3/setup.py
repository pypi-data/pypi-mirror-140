import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='Topsis_Paryagdeep_101903573',
    version="0.0.3",
    author='Paryagdeep Singh',
    author_email='psingh4_be19@thapar.edu',
    description='TOPSIS is a method of compensatory aggregation that compares a set of alternatives by identifying '
                'weights for each criterion, normalising scores for each criterion and calculating the geometric '
                'distance between each alternative and the ideal alternative, which is the best score in each '
                'criterion.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Paryaxify/Topsis-Paryagdeep-101903573.git',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['pandas', 'openpyxl'],
    keywords=['TOPSIS', 'PANDAS', 'AGGREGATION'],
    package_dir={"": "src"},
    packages=['Topsis_Paryagdeep_101903573'],
    include_package_data=True,
    python_requires=">=3.10",
    entry_points={
        "console_scripts": ["Topsis-Paryagdeep-101903573 = Topsis_Paryagdeep_101903573.topsis_Paryagdeep:main"]
    },
)