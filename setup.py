from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="M3UClean",
    version="1.0.0",
    author="Sam Estrin",    
    description="A tool for validating and cleaning M3U playlists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samestrin/m3uclean",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "m3uclean=m3uclean.app:main",
        ],
    },
)