# Sumit-sdk



## Getting started

## Description

Sumit SDK is a Python package that allows users to interact with Sumit-AI API. This document describes how to install the SDK from a zip file and how to use its main features.

## Installation

### Step 1: Download the SDK

1. Navigate to the "Tags" section of the GitLab repository.
2. Find the desired version of the SDK and click on it.
3. Click on the "Download" button and select "ZIP" to download a zip file of the SDK.

### Step 2: Extract the ZIP File

Extract the downloaded zip file to a location of your choice. You can do this by right-clicking the zip file and selecting "Extract All..." (the exact option might vary depending on your operating system).

### Step 3: Install the SDK

Open a terminal and navigate to the directory where the zip file was extracted. The SDK can be installed using _pip_ by running the following command:

```sh
cd path/to/extracted/folder
pip install .
```

_depracted:   
using `setup.py` installation with: `python setup.py install` is depracted and not supported in new python versions_

#### Install on Windows  
installation of: PyAudio, pyalsaaudio may failed in Windows. In this case the installation of all required library will failed. So in this case please install the required packages via pip: 
```pip install -r requirements.txt```  
