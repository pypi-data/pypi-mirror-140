from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="rac_api_client",
    url="https://github.com/RockefellerArchiveCenter/rac_api_client",
    description="A client to interact with the Rockefeller Archive Center's Collections API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rockefeller Archive Center",
    author_email="archive@rockarch.org",
    version="0.1.1",
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
    ],
)
