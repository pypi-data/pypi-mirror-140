import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="atomqc",  # Replace with your own username
    version="2021.10.11",
    author="Kamal Choudhary",
    author_email="kamal.choudhary@nist.gov",
    description="atomqc",
    install_requires=[
        "numpy>=1.19.5",
        "scipy>=1.6.3",
        "jarvis-tools>=2021.07.19",
        "qiskit",
        "scikit-learn>=0.24.1",
        "matplotlib>=3.4.1",
        "seaborn>=0.11.2",
        "tqdm>=4.60.0",
        "pandas==1.2.4",
        "pydantic>=1.8.1",
        "flake8>=3.9.1",
        "pycodestyle>=2.7.0",
        "pydocstyle>=6.0.0",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/usnistgov/atomqc",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
