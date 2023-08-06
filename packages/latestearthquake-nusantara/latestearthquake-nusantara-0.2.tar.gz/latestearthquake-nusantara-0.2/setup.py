"""
https://packaging.python.org/en/latest/tutorials/packaging-projects/
https://www.markdownguide.org/cheat-sheet/
"""
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="latestearthquake-nusantara",
    version="0.2",
    author="Muhammad Ihsan",
    author_email="muhammadihsan3011@gmail.com",
    description="This package will get the latest earthquake from BMKG | Meteorogical, Climatological, and "
                "Geophysical Agency",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mohehsan/latest-earthquake",
    project_urls={
        "Website": "https://www.mohammed-ehsan.com/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    # package_dir={"": "src"},
    # packages=setuptools.find_packages(where="src"),
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
