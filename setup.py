from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setup(
    name="sumit_sdk",
    # version="1.2.1",
    use_scm_version={
        "local_scheme": "no-local-version", 
    },
    setup_requires=['setuptools_scm'],
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "websocket-client>=1.5.0",
        "retry>=0.9.2",
        "python-socketio>=5.10.0",
        "numpy>=1.24.0,<2.0.0",
    ],
    extras_require={
        "audio": ["PyAudio", "pyalsaaudio"],  # Optional dependencies
    },
    python_requires=">=3.10",
    author="Sumit-AI",
    license="BSD-3",
    author_email="shlomi@sumit-ai.com",
    description="SDK to communicate with sumit API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.sumit-x.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: BSD-3 License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
)
