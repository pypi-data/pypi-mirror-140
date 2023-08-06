import setuptools

long_description = """# Topsis_Disha

Topsis_Disha is a library for calculating topsis score and ranking them according to the score.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install this package.

```bash
pip install Topsis-Disha-101903291
```

## Code Snippet

```python
from topsis import main
main()
```

## Usage in terminal

```python
python <filename.py> <data.csv> '1,1,1,1,1' '+,+,-,+,+' <result.csv>
```

## Input file (data.csv)

In this script, the first column should be named 'Fund Name' for the script to work correctly

| Fund Name | P1   | P2   | P3   | P4    |
| --------- | ---- | ---- | ---- | ----- |
| M1        | 0.79 | 0.62 | 1.25 | 60.89 |
| M2        | 0.66 | 0.44 | 2.89 | 63.07 |
| M3        | 0.56 | 0.31 | 1.57 | 62.87 |
| M4        | 0.82 | 0.67 | 2.68 | 70.19 |
| M5        | 0.75 | 0.56 | 1.3  | 80.39 |

## Output file (result.csv)

| Fund Name | P1   | P2   | P3   | P4    | Topsis Score | Rank |
| --------- | ---- | ---- | ---- | ----- | ------------ | ---- |
| M1        | 0.79 | 0.62 | 1.25 | 60.89 | 0.7722       | 2    |
| M2        | 0.66 | 0.44 | 2.89 | 63.07 | 0.2255       | 5    |
| M3        | 0.56 | 0.31 | 1.57 | 62.87 | 0.4388       | 4    |
| M4        | 0.82 | 0.67 | 2.68 | 70.19 | 0.5238       | 3    |
| M5        | 0.75 | 0.56 | 1.3  | 80.39 | 0.8113       | 1    |

The output file contains columns of input file along with two additional columns having **Topsis Score** and **Rank**
"""

setuptools.setup(
    name="Topsis-Disha-101903291",
    version="0.0.6",
    author="Disha Sharma",
    author_email="dsharma2_be19@thapar.edu",
    description="Get topsis score",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/disha0602/topsis-py",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    py_modules=["topsis"],
    include_package_data=True,
    install_requires='pandas'
)