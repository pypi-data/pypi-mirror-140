from pathlib import Path
from setuptools import setup, find_packages

setup(
    # Package info
    name="inmanta-tfplugin",
    version="5.2.0",
    author="Inmanta",
    author_email="code@inmanta.com",
    url="https://github.com/inmanta/inmanta-tfplugin",
    license="MPL 2.0",
    description="Auto generated python package for Terraform Plugin RPC protocol",
    long_description_content_type="text/markdown",
    long_description=Path("README.md").read_text(),

    # Package content
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=Path("requirements.txt").read_text().split("\n"),
    entry_points={"pytest11": ["inmanta-tfplugin = inmanta_tfplugin"]},
)
