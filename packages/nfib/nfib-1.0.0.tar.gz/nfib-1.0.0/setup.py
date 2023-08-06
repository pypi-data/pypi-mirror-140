from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="nfib",  # Required
    version="1.0.0",  # Required
    author="neha",  # Optional
    author_email="neha.patil@crestdatasys.com",  # Optional
    description="   Fibonacci Package which returns nth fibonacci number",  # Optional
    long_description=long_description,  # Optional
    keywords=" setuptools, development",  # Optional
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),  # Required
    python_requires=">=3.6, <4",
    entry_points={  # Optional
        "console_scripts": [
            "Packaging=Fibonacci.Function.n_fibonacci:main",
        ],
    },
)
