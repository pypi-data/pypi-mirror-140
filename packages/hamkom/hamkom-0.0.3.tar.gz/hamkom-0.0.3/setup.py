import setuptools

setuptools.setup(
    name="hamkom",
    version="0.0.3",
    author="Marcel Miljak",
    author_email="mmiljak@tsn.at",
    description="Package for hamster-communication",
    install_requires=[            # I get to this in a second
      'msgpack>1'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "hamsterkmn"},
    packages=setuptools.find_packages(where="hamsterkmn"),
    python_requires=">=3.6",
)
