import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "aws-prototyping-sdk",
    "version": "0.0.13",
    "description": "aws-prototyping-sdk",
    "license": "Apache-2.0",
    "url": "https://github.com/aws/aws-prototyping-sdk",
    "long_description_content_type": "text/markdown",
    "author": "AWS APJ COPE<apj-cope@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/aws/aws-prototyping-sdk"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "aws-prototyping-sdk",
        "aws-prototyping-sdk._jsii",
        "aws-prototyping-sdk.pdk_pipeline",
        "aws-prototyping-sdk.pdk_projen"
    ],
    "package_data": {
        "aws-prototyping-sdk._jsii": [
            "aws-prototyping-sdk@0.0.13.jsii.tgz"
        ],
        "aws-prototyping-sdk": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii>=1.54.0, <2.0.0",
        "projen>=0.52.31, <0.53.0",
        "publication>=0.0.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
