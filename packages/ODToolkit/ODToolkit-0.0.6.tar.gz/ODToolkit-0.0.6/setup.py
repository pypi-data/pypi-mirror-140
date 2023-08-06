import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

REQUIREMENTS = ["tqdm", "opencv-python", "behave", "sure"]

setuptools.setup(
    name = "ODToolkit",
    url='https://github.com/BarCodeReader/ODToolkit',
    version="0.0.6",
    author = "YUN_Yi_Ke",
    author_email='assassin@gs-roobt.com',
    description = "An object detection toolkit for data mining and visualization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["ODToolkit"],
    python_requires=">=3.6",
    install_requires=REQUIREMENTS,
)