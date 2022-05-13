**This project is in no way associated with LernSax, WebWeaver, DigiOnline GmbH or Freistaat Sachsen**

## What is this?

This is an API Wrapper for the LernSax API using pyodide.http to allow usage in PyScript. Please note that we do not encourage taking any harmful actions against anyone using this wrapper.

## Usage
Copy the [basic HTML skeleton](./base.html) and paste the main.py in the directory containing your script and html files, just like in the examples

## Documentation?
Basic Documentation, generated with pdoc, for the original is available [here](https://okok7711.github.io/lernsax/)
For Documentation of the actual LernSax jsonrpc API you should probably still stick to  [this repo](https://github.com/TKFRvisionOfficial/lernsax-webweaver-api-research)

## Example Usage
Look at the examples in the examples folder!

## Accessing Files via WebDav
This module does not have support for DAV for now. This is due to aiohttp and therefore aiodav not working with pyodide.