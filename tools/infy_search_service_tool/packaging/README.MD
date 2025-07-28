
# Infy Search Service Tool (Python Wrapper)

The `infy_search_service_tool` is originally a set of static HTML files. 
To run in python ecosystem, it's wrapped inside a python project and distributed as a python library i.e. wheel file.

## Build the Library (as a creator/developer)

Double click to run below script file.

```dos
BuildPackage.bat
```

## Use the Library (as a consumer/client)

Install the package into a client python virtual environment by running below in terminal.

```dos
pip install infy_search_service_tool-x.x.x-py3-none-any.whl
```

To start the service, run the following command from termninal.

```dos
infy_search_service_tool start
```

> NOTE: To stop the service, press `Ctrl+C` in same terminal.


For available options, use `help` option.

```dos
infy_search_service_tool --help
```

