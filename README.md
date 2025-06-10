# Google Maps Geocoding API Script
A lightweight Python script for accessing the Google Maps Geocoding API, supporting both direct API requests and browser-based lookups.

## Table of Contents

* [Installation](#installation)
* [Usage](#usage)

## Installation

To install the client, run the following command:
```bash
pip install -r requirements.txt
```

This will install the required dependencies, including the requests and selenium libraries.

## Usage
To use the client, simply import the get_coordinates function and call it with a location string:

```python
from geocoding_client import get_coordinates

location = "New York, NY"
coordinates = get_coordinates(location)
print(coordinates)
```
This will print the latitude and longitude of the location.

Alternatively, ensure that there is a /data directory or set the excel_path in the main function and run:
```bash
python location_finder.py
```
