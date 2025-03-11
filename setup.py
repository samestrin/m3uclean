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
        "certifi==2025.1.31",
        "charset-normalizer==3.4.1",
        "idna==3.10",
        "requests==2.32.3",
        "tenacity==9.0.0",
        "urllib3==2.3.0",
    ],
    entry_points={
        "console_scripts": [
            "m3uclean=m3uclean.app:main",
        ],
    },
)