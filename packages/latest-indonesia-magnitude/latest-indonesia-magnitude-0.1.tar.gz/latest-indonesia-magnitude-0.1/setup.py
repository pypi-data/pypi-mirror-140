'''
https://packaging.python.org/en/latest/tutorials/packaging-projects/
'''
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="latest-indonesia-magnitude",
    version="0.1",
    author="Malik Akbar",
    author_email="alee@vescod.com",
    description="This package will get the latest eartquake in indonesia from BMKG",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mas-Akbar/latest-indonesia-magnitude",
    project_urls={
        "Website": "https://vescod.com",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
    ],
    # package_dir={"": "src"},
    # packages=setuptools.find_packages(where="src"),
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
