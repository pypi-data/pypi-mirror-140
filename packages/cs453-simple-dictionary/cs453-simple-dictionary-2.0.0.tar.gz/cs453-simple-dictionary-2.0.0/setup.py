from setuptools import setup

setup(
    name="cs453-simple-dictionary",
    author="Mehmet Çalışkan",
    version="2.0.0",
    packages=["dictionary"],
    install_requires=[
        "requests>=2.23.0",
    ],
    python_requires=">=3.8",

)
