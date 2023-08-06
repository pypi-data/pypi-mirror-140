try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


import setuptools


setuptools.setup(
    name="algora-sdk",
    version_format='{tag}.{commits}',
    setup_requires=['very-good-setuptools-git-version'],
    author="Algora Labs",
    author_email="support@algoralabs.com",
    description="Algora Labs Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://docs.algoralabs.com",
    packages=setuptools.find_packages(exclude=["*.test", "*.test.*", "test.*", "test", "ALGORA_README.md"]),
    package_data={'config': ['config.yml']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7",
    # TODO: Add version requirements to packages
    install_requires=[
        "pandas",
        "pypandoc",
        "pytest",
        "requests",
        "cachetools",
        "pydash",
        "PyYaml",
        "scipy"
    ]
)
