import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "serverless-container-constructs",
    "version": "0.1.20",
    "description": "CDK patterns for modern application with serverless containers on AWS",
    "license": "UNLICENSED",
    "url": "https://github.com/aws-samples/serverless-container-constructs",
    "long_description_content_type": "text/markdown",
    "author": "Pahud Hsieh<hunhsieh@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/aws-samples/serverless-container-constructs"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "serverless_container_constructs",
        "serverless_container_constructs._jsii"
    ],
    "package_data": {
        "serverless_container_constructs._jsii": [
            "serverless-container-constructs@0.1.20.jsii.tgz"
        ],
        "serverless_container_constructs": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib>=2.11.0, <3.0.0",
        "cdk-nag>=2.0.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.54.0, <2.0.0",
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
        "Development Status :: 5 - Production/Stable"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
