from setuptools import setup, find_packages

setup(
    name="sumit_sdk",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "websocket-client",
        "retry"
    ],
    author="Sumit-AI",
    author_email="shlomi@sumit-ai.com",
    description="SDK to communicate with sumit API",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="",
)
