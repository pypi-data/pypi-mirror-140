from pathlib import Path
from setuptools import setup

here = Path(__file__).parent
README = here.joinpath("README.md").read_text()

setup(
    name="feature-test",
    version="0.1.13",
    description="examines the relationships between a new feature and everyother feature in a dataset",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.cee.redhat.com/twileman/feature_test",
    author="Thomas Wilmean",
    author_email="twileman@redhat.com",
    license="MIT License",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
