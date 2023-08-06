import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycord-paging",
    version="1.0.0",
    author="Tommodev",
    license="MIT",
    description="Pycord paginator for messages and embeds with reactions or buttons.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tommodev-06/pycord-paging",
    project_urls={
        "Source": "https://github.com/Tommodev-06/pycord-paging",
        "Documentation": "https://tommodev.gitbook.io/pycord-paging/"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    install_requires=['aiohttp', 'py-cord==2.0.0b4', 'asyncio'],
    keywords='pycord paginator pycord-paginator',
    packages=setuptools.find_packages(include=['paginator', 'paginator.*']),
    python_requires=">=3.6",
)
