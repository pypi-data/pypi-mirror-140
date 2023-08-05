# Labii SDK

An SDK for the [Labii ELN & LIMS platform](https://www.labii.com) that provides interaction with the [Labii API](https://docs.labii.com/api/overview).

![Labii screenshot](https://www.labii.com/media/screenshots/labii-richtext-editor.webp)

This package contains two modules, __api_client__ and __sdk__.
* Python API clients help you perform Labii API calls, such as authentication, get, patch, post, and delete. Learn more at [APICLIENT.md](https://gitlab.com/labii-dev/labii-sdk/-/blob/master/docs/APICLIENT.md)
* SDK is the toolkit with prebuilt Labii components that developers use to interact with Labii APIs. Learn more at [SDK.md](https://gitlab.com/labii-dev/labii-sdk/-/blob/master/docs/SDK.md)

# Install
```
pip install labii-sdk
```

# Usage
```python
# 1. Install the Labii SDK
pip install labii-sdk

# 2. Import the package
from labii_sdk.sdk import LabiiObject

# 3. Initial the API object
labii = LabiiObject()

# 4. Start querying
labii.api.login()
# get a list of tables
labii.Tables.list()
```

# Documentation
* [Labii API documentation](https://docs.labii.com/api/overview)
* [Labii API Client documentation](https://gitlab.com/labii-dev/labii-sdk/-/blob/master/docs/APICLIENT.md)
* [Labii SDK documentation](https://gitlab.com/labii-dev/labii-sdk/-/blob/master/docs/SDK.md)

# About Labii
[Labii](https://www.labii.com) facilitates research and development by providing a user-friendly, customizable Electronic Lab Notebook (ELN) and Laboratory Information Management System (LIMS) to document, manage, and interpret data. Labii ELN & LIMS can be configured for any type of data, and the functions can easily be enhanced and expanded by stand-alone applications. We address the unique needs of each of our customers and are the trusted provider of hundreds of biotech companies and academic labs.
