# pyAdsWebService

## Synopsis

This project contains Python wrapper functions used to Read and Write values from/to a TwinCat PLC configuration (Beckhoff).  It allows multiple clients to seamlessly communicate with the configuration without having to install TwinCat and configure an aDS route on each of these clients.  

Note that an ADS Web Service must be configured on a PC server for these functions to work.  Information on how to configure a TwinCat web server can be found here:

https://infosys.beckhoff.com/english.php?content=../content/1033/tcadswebservice/html/WebService_Install_XP.htm&id=

## Code Example

### Read one variable

pyadswebservice.ReadADSWeb([["Main.INT_test", "INT"]], "192.165.1.65", "5.29.121.198.1.1", 851)

### Read multiple variables

pyadswebservice.ReadADSWeb([["Main.INT_test", "INT"],["Main.DINT_test", "DINT"]],  "192.165.1.65", "5.29.121.198.1.1", 851)

[10, 23]


### Write one variable

pyadswebservice.WriteADSWeb([["Main.DINT_test",13, "DINT"]],  "192.165.1.65", "5.29.121.198.1.1", 851)

### Write multiple variables

pyadswebservice.WriteADSWeb([["Main.DINT_test",13, "DINT"],["Main.INT_test",11, "INT"]],  "192.165.1.65", "5.29.121.198.1.1", 851)

## Installation

Download the package and install using the command:

python setup.py install

## License

Copyright (c) 2017 Guillaume Robichaud

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
