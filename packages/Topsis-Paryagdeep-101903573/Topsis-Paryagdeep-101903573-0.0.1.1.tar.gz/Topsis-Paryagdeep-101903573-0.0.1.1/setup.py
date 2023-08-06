# from setuptools import setup, find_packages
#
# setup(
#     name='Topsis-Paryagdeep-101903573',
#     packages=find_packages('Topsis-Paryagdeep-101903573'),
#     version='0.0.1',
#     license='MIT',
#     description='TOPSIS is a method of compensatory aggregation that compares a set of alternatives by identifying '
#                 'weights for each criterion, normalising scores for each criterion and calculating the geometric '
#                 'distance between each alternative and the ideal alternative, which is the best score in each '
#                 'criterion.',
#     author='Paryagdeep Singh',
#     author_email='psingh_4be19@thapar.edu',
#     # package_dir={'': ''},
#     url='https://github.com/Paryaxify/Topsis-Paryagdeep-101903573.git',
#     download_url='https://github.com/Paryaxify/Topsis-Paryagdeep-101903573/archive/refs/tags/Topsis0.0.1.tar.gz',
#     keywords=['TOPSIS', 'PANDAS', 'AGGREGATION'],
#     install_requires=[
#         'pandas'
#     ],
#     classifiers=[
#         'Development Status :: 3 - Alpha',
#         'Intended Audience :: Developers',
#         'License :: OSI Approved :: MIT License',
#         'Programming Language :: Python :: 3.10',
#     ],
# )


import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='Topsis-Paryagdeep-101903573',
    version="0.0.1.1",
    author='Paryagdeep Singh',
    author_email='psingh_4be19@thapar.edu',
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
    install_requires=[
        'pandas'
    ],
    keywords=['TOPSIS', 'PANDAS', 'AGGREGATION'],
    packages=setuptools.find_packages(where="Topsis-Paryagdeep-101903573"),
    python_requires=">=3.10",
)