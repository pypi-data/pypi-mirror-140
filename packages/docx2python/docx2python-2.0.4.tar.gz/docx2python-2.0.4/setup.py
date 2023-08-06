import setuptools

with open("README.md") as fh:
    long_description = fh.read()

requirements = ['lxml']

setuptools.setup(
    name="docx2python",
    version="2.0.4",
    author="Shay Hill",
    author_email="shay_public@hotmail.com",
    description="Extract content from docx files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ShayHill/docx2python",
    install_requires=requirements,
    extras_require={'dev': ['pytest']},
    packages=setuptools.find_packages(exclude=['Test', 'test*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)



