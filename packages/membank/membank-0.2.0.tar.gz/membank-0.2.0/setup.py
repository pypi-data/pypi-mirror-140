import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

    setuptools.setup(
        name="membank",
        version="0.2.0",
        author="Juris Kaminskis",
        author_email="juris.kaminskis@gmail.com",
        description="A package to handle persistent memory",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/Kolumbs/membank",
        project_urls={
            "Bug Tracker": "https://github.com/Kolumbs/membank/issues",
        },
        classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        ],
        packages=setuptools.find_packages(where="membank"),
        python_requires=">=3.6",
)
