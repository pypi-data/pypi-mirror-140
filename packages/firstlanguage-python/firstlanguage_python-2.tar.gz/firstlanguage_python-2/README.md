
# Getting Started with FirstLanguage API

## Introduction

Collection of NLP APIs to help developers. We have grouped the APIs under Basic and Advanced. Basic APIs cover all basic text operations like POSTag, Stemmer etc and Advanced cover all the APIs like QA, translation etc.

### OpenAPI Specification

This API is documented in **OpenAPI v3.0 format**.
In addition to standard
OpenAPI syntax we use a few [vendor extensions](https://github.com/Redocly/redoc/blob/master/docs/redoc-vendor-extensions.html).

## Building

You can use the SDK either from source by cloning from GitHub using our [repo](https://github.com/FirstLanguage/firstlanguage_python.git)

Or you can use PIP to install our package directly by using the command.

```
pip install firstlanguage-python
```

## Follow below steps if you want to use SDK from our PIP published package

Once the package is installed you can directly use our package in your code. Below is a working example. Replace <Your_API_KEY> with your API Key from the dashboard.

```
from firstlanguage_python.firstlanguage_client import Client
from firstlanguage_python.configuration import Environment
import jsonpickle


client = Client(
    apikey='<Your_API_KEY>',
    environment=Environment.PRODUCTION,)

reqbody='{"input":{"text":"அவள் வேகமாக ஓடினாள்","lang":"ta"} }'

body = jsonpickle.decode(reqbody)
basic_api_controller = client.basic_api

result = basic_api_controller.get_stemmer(body)

for res in result:
  print("Original Text passed: "+res.orginal_text)
  print("Stemmed result: "+res.stem)


```

Save the above file as test.py and run it using the below command

```
python3 test.py
```

You will get an output like below

```
200
Original Text passed: அவள்
Stemmed result: அவள்
Original Text passed: வேகமாக
Stemmed result: வேகம்
Original Text passed: ஓடினாள்
Stemmed result: ஓடி
```

## Follow below steps if you want to use SDK from source

You must have Python `3 >=3.7, <= 3.9` installed on your system to install and run this SDK. This SDK package depends on other Python packages like nose, jsonpickle etc. These dependencies are defined in the `requirements.txt` file that comes with the SDK. To resolve these dependencies, you can use the PIP Dependency manager. Install it by following steps at [https://pip.pypa.io/en/stable/installing/](https://pip.pypa.io/en/stable/installing/).

Python and PIP executables should be defined in your PATH. Open command prompt and type `pip --version`. This should display the version of the PIP Dependency Manager installed if your installation was successful and the paths are properly defined.

* Using command line, navigate to the directory containing the generated files (including `requirements.txt`) for the SDK.
* Run the command `pip install -r requirements.txt`. This should install all the required dependencies.

![Building SDK - Step 1](https://apidocs.io/illustration/python?workspaceFolder=Firstlanguageapi-Python&step=installDependencies)

## Installation

The following section explains how to use the firstlanguageapi library in a new project.

### 1. Open Project in an IDE

Open up a Python IDE like PyCharm. The basic workflow presented here is also applicable if you prefer using a different editor or IDE.

![Open project in PyCharm - Step 1](https://apidocs.io/illustration/python?workspaceFolder=Firstlanguageapi-Python&step=pyCharm)

Click on `Open` in PyCharm to browse to your generated SDK directory and then click `OK`.

![Open project in PyCharm - Step 2](https://apidocs.io/illustration/python?workspaceFolder=Firstlanguageapi-Python&step=openProject0)

The project files will be displayed in the side bar as follows:

![Open project in PyCharm - Step 3](https://apidocs.io/illustration/python?workspaceFolder=Firstlanguageapi-Python&projectName=firstlanguageapi&step=openProject1)

### 2. Add a new Test Project

Create a new directory by right clicking on the solution name as shown below:

![Add a new project in PyCharm - Step 1](https://apidocs.io/illustration/python?workspaceFolder=Firstlanguageapi-Python&projectName=firstlanguageapi&step=createDirectory)

Name the directory as "test".

![Add a new project in PyCharm - Step 2](https://apidocs.io/illustration/python?workspaceFolder=Firstlanguageapi-Python&step=nameDirectory)

Add a python file to this project.

![Add a new project in PyCharm - Step 3](https://apidocs.io/illustration/python?workspaceFolder=Firstlanguageapi-Python&projectName=firstlanguageapi&step=createFile)

Name it "testSDK".

![Add a new project in PyCharm - Step 4](https://apidocs.io/illustration/python?workspaceFolder=Firstlanguageapi-Python&projectName=firstlanguageapi&step=nameFile)

In your python file you will be required to import the generated python library using the following code lines

```python
from firstlanguageapi.firstlanguageapi_client import FirstlanguageapiClient
```

![Add a new project in PyCharm - Step 5](https://apidocs.io/illustration/python?workspaceFolder=Firstlanguageapi-Python&projectName=firstlanguageapi&libraryName=firstlanguageapi.firstlanguageapi_client&className=FirstlanguageapiClient&step=projectFiles)

After this you can write code to instantiate an API client object, get a controller object and  make API calls. Sample code is given in the subsequent sections.

### 3. Run the Test Project

To run the file within your test project, right click on your Python file inside your Test project and click on `Run`

![Run Test Project - Step 1](https://apidocs.io/illustration/python?workspaceFolder=Firstlanguageapi-Python&projectName=firstlanguageapi&libraryName=firstlanguageapi.firstlanguageapi_client&className=FirstlanguageapiClient&step=runProject)

## Test the SDK

You can test the generated SDK and the server with test cases. `unittest` is used as the testing framework and `nose` is used as the test runner. You can run the tests as follows:

Navigate to the root directory of the SDK and run the following commands

```
pip install -r test-requirements.txt
nosetests
```

## Initialize the API Client

**_Note:_** Documentation for the client can be found [here.](/doc/client.html)

The following parameters are configurable for the API Client:

| Parameter | Type | Description |
|  --- | --- | --- |
| `apikey` | `string` | API Key can be copied from your dashboard |
| `http_client_instance` | `HttpClient` | The Http Client passed from the sdk user for making requests |
| `override_http_client_configuration` | `bool` | The value which determines to override properties of the passed Http Client from the sdk user |
| `timeout` | `float` | The value to use for connection timeout. <br> **Default: 60** |
| `max_retries` | `int` | The number of times to retry an endpoint call if it fails. <br> **Default: 0** |
| `backoff_factor` | `float` | A backoff factor to apply between attempts after the second try. <br> **Default: 2** |
| `retry_statuses` | `Array of int` | The http statuses on which retry is to be done. <br> **Default: [408, 413, 429, 500, 502, 503, 504, 521, 522, 524]** |
| `retry_methods` | `Array of string` | The http methods on which retry is to be done. <br> **Default: ['GET', 'PUT']** |

The API client can be initialized as follows:

```python
from firstlanguageapi.firstlanguageapi_client import FirstlanguageapiClient
from firstlanguageapi.configuration import Environment

client = FirstlanguageapiClient(
    apikey='apikey',
    environment=Environment.PRODUCTION,)
```

## Authorization

This API uses `Custom Header Signature`.

## List of APIs

* [Basic APIs](/doc/controllers/basic-api.html)
* [Advanced APIs](/doc/controllers/advanced-api.html)

## Classes Documentation

* [Utility Classes](/doc/utility-classes.html)
* [HttpResponse](/doc/http-response.html)
* [HttpRequest](/doc/http-request.html)

