import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Tinycord",
    version="0.3.0",
    author="xArty",
    author_email="email@xarty.xyz",
    description="Easy and flexible Discord wrapper built on aiohttp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tinycord/Tinycord",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows',
        "Operating System :: MacOS",
        "Operating System :: Unix",
    ],
    install_requires=['aiohttp'],
    packages=setuptools.find_packages('.'),
    python_requires=">=3.6",
)