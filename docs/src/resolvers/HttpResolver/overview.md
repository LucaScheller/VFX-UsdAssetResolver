# Http Resolver (arHttp @charlesfleche)

This is a proof of concept http resolver. This is kindly provided and maintained by @charlesfleche in the [arHttp: Offloads USD asset resolution to an HTTP server
](https://github.com/charlesfleche/arHttp) repository. 

For documentation, feature suggestions and bug reports, please file a ticket there. 

This repo handles the auto-compilation against DCCs and exposing to the automatic installation update manager UI.

## Running the demo server
As the resolver reacts to http requests, we need to setup a local server to answer to our requests.

~~~admonish tip
This can be easily done by running:
- <install/dist root folder>/httpResolver/demo/server_install.sh/.bat file to create the python virtual environment with the necessary packages
- <install/dist root folder>/httpResolver/demo/server_launch.sh/.bat file to run the demo server
~~~

~~~admonish warning
Please make sure that you have python installed at the system level and available on your "PATH" environment variable.
Our install scripts use it to create a virtual environment that runs the http demo server.
~~~