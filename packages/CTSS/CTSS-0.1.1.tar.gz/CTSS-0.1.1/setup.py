import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CTSS",
    version="0.1.1",
    author="Mikhail Kurbakov",
    author_email="muwa1997@mail.ru",
    description="Software package for the CT&SS laboratory of Tula State University",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['numpy>=1.21'],
    url="https://github.com/muwsik",
    #project_urls={
    #    "tag": "url",
    #},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.*",
)