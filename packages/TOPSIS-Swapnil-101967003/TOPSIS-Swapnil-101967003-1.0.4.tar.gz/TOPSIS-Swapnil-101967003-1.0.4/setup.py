from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README

setup(
    name="TOPSIS-Swapnil-101967003",
    packages=["Topsis_Ranking"],
    version="1.0.4",
    license="MIT",
    description="A Python package to get best alternative available using TOPSIS method.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Swapnil Kumar Singh",
    author_email="ssingh19_be19@thapar.edu",
    classifiers=[
        "Development Status :: 3 - Alpha",      
        "Intended Audience :: Developers",  
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    include_package_data=True,
    install_requires=["pandas"],
    entry_points={
        "console_scripts": [
            "TOPSIS-Swapnil-101967003=Topsis_Ranking.topsis:main",
        ]
    },
)