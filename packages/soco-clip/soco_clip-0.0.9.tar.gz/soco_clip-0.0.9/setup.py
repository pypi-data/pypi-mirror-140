import setuptools
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="soco_clip",
    packages = find_packages(),
    package_data={'soco_clip': ['soco_clip/models/configs/*.yaml','*.gz']},
    include_package_data=True,
    version="0.0.9",
    author="kyusonglee",
    description="OpenAI CLIP wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.soco.ai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Free for non-commercial use",
        "Operating System :: OS Independent",
    ],
    install_requires = [
        "pytorch_lightning",
        "transformers",
        "torch",
        "torchvision",
        "ftfy",
        "opencv-python"
    ]
)
