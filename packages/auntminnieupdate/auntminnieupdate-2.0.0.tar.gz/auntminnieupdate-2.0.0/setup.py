import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="auntminnieupdate",
    version="2.0.0",
    author="Sencho Parameswara",
    author_email="senchoparameswara@gmail.com",
    description="this package for scraping auntminnie recent news, webinars and radiology conference",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/senchooo/auntminnnie-update",
    project_urls={
        "MyWeb": "https://senchooo.com",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta"
    ],
    packages=["auntminnieupdate"],
    python_requires=">=3.6"
)
