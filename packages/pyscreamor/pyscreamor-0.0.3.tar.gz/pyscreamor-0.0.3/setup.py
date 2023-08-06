import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyscreamor",
    version="0.0.3",
    author="Devecor",
    author_email="devecor@163.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://devecor.cn",
    project_urls={
        "Bug Tracker": "https://devecor.cn",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    package_data={
        "pyscreamor": ["pyscreamor.service"]
    },
    install_requires=[
        "paho-mqtt>=1.6.1"
    ],
    python_requires=">=3.6",
)
