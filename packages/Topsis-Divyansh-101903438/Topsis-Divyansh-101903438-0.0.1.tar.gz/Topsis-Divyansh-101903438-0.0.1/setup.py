from matplotlib.pyplot import install_repl_displayhook
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Topsis-Divyansh-101903438",
    version="0.0.1",
    author="Divyansh Purohit",
    author_email="dpurohit_be19@thapar.edu",
    description="topsis implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    install_requires=["numpy", "pandas"],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
