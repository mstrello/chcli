# chcli

A CLI tool for quering the API from CloudHealth.

It uses [click](https://click.palletsprojects.com/en/7.x/) package to work with options and arguments to the command, 
and [requests](https://requests.readthedocs.io/en/master/) package for consulting the REST API offered by CloudHealth.

The CloudHealth API is (not so well) documented [here](https://apidocs.cloudhealthtech.com/).

The tool uses the CH_API_KEY environment variable for saving the CloudHealth API key. This variable must be
settled before using it.
