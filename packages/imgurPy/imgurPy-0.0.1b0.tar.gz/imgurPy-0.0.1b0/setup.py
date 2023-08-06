from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="imgurPy",
    version="0.0.1beta",
    author="ThanatosDi",
    author_email="ThanatosDi@kttsite.com",
    description="imgur python library (not official)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ThanatosDi/imgurPy",
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [

        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Win32 (MS Windows)",
        "Topic :: Documentation :: Sphinx",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries",
        ""
    ],
)