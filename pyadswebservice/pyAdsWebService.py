import requests
import base64
import xml.etree.ElementTree as ET
import struct

def getvariablehandles(names, url, netID, port):
    """
    :summary: Returns byte array containing variable handler information.

    :param list names: list of variable names (e.g. ['Main.var1, 'Main.var2'])
    :param string url: WebService address
    :param string netID: AmsAddr of configuration
    :param int port: ADS port
    :param int plc_datatype: datatype, according to PLCTYPE constants

    """

    #Unpack inputs and define Variables
    numberOfVariables=len(names)

    #Define ReadWrite request's indexGroup for Reading values from PLC
    indexGroup=61570

    #Define index memory allocation
    indexOffset=1*numberOfVariables
    cbrLen=12*numberOfVariables

    #Define the query header
    handleQueryHeader=[[3, 240, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, len(name), 0, 0, 0] for name in names]

    #Define the query tail, variable name as a list of 0-255 ascii characters
    handleQueryVariableName=[[ord(char) for char in name] for name in names]

    #Both lists are joined and flatten
    handleQueryArray =flatten(handleQueryHeader+handleQueryVariableName);

    #List is encoded as a base64 binary string array
    base64EncodedStr = base64.b64encode(bytearray(handleQueryArray)).decode('ascii')

    #Construct web request
    headers = {'content-type': 'text/xml'}
    body = """<?xml version="1.0" encoding="UTF-8"?>
             <SOAP-ENV:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance/" xmlns:xsd="http://www.w3.org/2001/XMLSchema/"
                xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                <SOAP-ENV:Body><q1:ReadWrite xmlns:q1="http://beckhoff.org/message/">
          <netId xsi:type="xsd:string">"""+netID+"""</netId>
          <nPort xsi:type="xsd:int">"""+str(port)+"""</nPort><indexGroup xsi:type="xsd:unsignedInt">"""+str(indexGroup)+"""</indexGroup><indexOffset xsi:type="xsd:unsignedInt">"""+str(indexOffset)+"""</indexOffset>" +
            <cbRdLen xsi:type="xsd:int">"""+str(cbrLen)+"""</cbRdLen><pwrData xsi:type="xsd:base64Binary">"""+base64EncodedStr+"""</pwrData>"
          </q1:ReadWrite></SOAP-ENV:Body></SOAP-ENV:Envelope>"""

    #Send request and parse reponse
    response = requests.post(url,data=body,headers=headers)
    tree = ET.ElementTree(ET.fromstring(response.content.decode('ascii')))
    root = tree.getroot()


    #Check for error code and return it if one is found
    errorcode=root.find('.//{http://beckhoff.org}errorcode')
    if errorcode!=None:
        errorNo=root.find('.//{http://beckhoff.org}errorcode').text
        print("TwinCAT error "+errorNo+ " encountered while retrieving handles: " +errorCode(int(errorNo)))
        return(0)

    #Extract the response and convert to array
    outputBinary=root.find('*//ppRdData').text
    outputArray=[c for c in base64.b64decode(outputBinary)]

    rawheaders=outputArray[0:len(names)]

    #Extract error codes from headers
    responseHeaderCodes =[int.from_bytes(rawheaders[i:i + 2], byteorder='little', signed=False)  for i in range(0, len(rawheaders), 8)]
    for code in responseHeaderCodes:
        if code!=0:
            print("TwinCAT error "+str(code)+ " encountered while retrieving handles: " +errorCode(code))
            return(0)



    return(outputArray)

def ReadADSWeb(readRequest, ip, netID, port):
    """
    :summary: Reads variable values on a Twincat configuration.

    :param list readRequest: Nested list of variable names and types (e.g. [['Main.var1', 'INT'], ['Main.var2', 'DINT']])
    :param string ip: WebService IP address
    :param string netID: AmsAddr of configuration
    :param int port: ADS port

    """
    #Define the web seb service url
    url="http://"+ip+"/TcAdsWebService/TcAdsWebService.dll"

    #Unpack inputs
    names=[x[0] for x in readRequest]
    vartypes=[x[1] for x in readRequest]

    #Extract number of variables
    numberOfVariables=len(readRequest)

    #Get the variable handle
    varHandle = getvariablehandles(names, url, netID, port)

    #Returns 0 if an error was encountered while requesting the variable handle
    if varHandle==0:
        return(0)


    #Define ReadWrite request's indexGroup for Reading values from PLC
    indexGroup=61568
    indexOffset=1*numberOfVariables


    #Use helper varbyte(x) to get the variable size from the
    varByteSize= [varbyte(x) for x in vartypes]

    #Extract the flat list of index offsets
    indexOffsetBytesFlat=varHandle[(-4*len(readRequest)):]

    #Split flat list of index offset in subgroup of 4, associated with each variables
    indexOffsetBytes=[indexOffsetBytesFlat[x:x+4] for x in range(0, len(indexOffsetBytesFlat), 4)]


    readQueryLists= [[5, 240, 0, 0, indexOffsetBytes[x], varByteSize[x], 0, 0, 0] for x in range(len(readRequest))]

    readQuery=flatten(readQueryLists)

    base64EncodedQuery = base64.b64encode(bytearray(readQuery)).decode('ascii')

    cbrLen=4*numberOfVariables+sum(varByteSize)


    headers = {'content-type': 'text/xml'}
    body = """<?xml version="1.0" encoding="UTF-8"?>
             <SOAP-ENV:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance/" xmlns:xsd="http://www.w3.org/2001/XMLSchema/"
                xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                <SOAP-ENV:Body><q1:ReadWrite xmlns:q1="http://beckhoff.org/message/">
          <netId xsi:type="xsd:string">"""+netID+"""</netId>
          <nPort xsi:type="xsd:int">"""+str(port)+"""</nPort><indexGroup xsi:type="xsd:unsignedInt">"""+str(indexGroup)+"""</indexGroup><indexOffset xsi:type="xsd:unsignedInt">"""+str(indexOffset)+"""</indexOffset>" +
            <cbRdLen xsi:type="xsd:int">"""+str(cbrLen)+"""</cbRdLen><pwrData xsi:type="xsd:base64Binary">"""+base64EncodedQuery+"""</pwrData>"
          </q1:ReadWrite></SOAP-ENV:Body></SOAP-ENV:Envelope>"""

    response = requests.post(url,data=body,headers=headers)
    tree = ET.ElementTree(ET.fromstring(response.content.decode('ascii')))

    root = tree.getroot()

    #Check for error code and return it if one is found
    errorcode=root.find('.//{http://beckhoff.org}errorcode')
    if errorcode!=None:
        errorNo=root.find('.//{http://beckhoff.org}errorcode').text
        print("TwinCAT error "+errorNo+ " encountered while retrieving handles: " +errorCode(int(errorNo)))
        return(0)

    #Extract the response and convert to array
    outputBinary=root.find('*//ppRdData').text
    outputArray=[c for c in base64.b64decode(outputBinary)]

    #
    valueByteArray=outputArray[-sum(varByteSize):]

    #Extract byte arrays for each requested variavles
    outputByteArrays=[valueByteArray[sum(varByteSize[:i]):sum(varByteSize[:i])+varByteSize[i]] for i in range(0,len(varByteSize))]

    #Convert byte array list to python bytearray
    byteArraysHex = [bytearray(x[::-1]) for x in outputByteArrays]

    #Convert the byte arrays to values using byteArrayToValue() helper function
    outputValue= [byteArrayToValue(byteArraysHex[x], vartypes[x]) for x in range(len(byteArraysHex))]

    return(outputValue)



def WriteADSWeb(writeRequest, ip, netID, port):
    """
    :summary: Write values on a Twincat configuration.

    :param list writeRequest: Nested list of variable names and types (e.g. [['Main.var1', 2, 'INT'], ['Main.var2', 4, 'DINT']])
    :param string ip: WebService IP address
    :param string netID: AmsAddr of configuration
    :param int port: ADS port

    """
    #Define the web seb service url
    url="http://"+ip+"/TcAdsWebService/TcAdsWebService.dll"

    #Unpack inputs
    names=[x[0] for x in writeRequest]
    newValues=[x[1] for x in writeRequest]
    vartypes=[x[2] for x in writeRequest]

    #Get the variable handle
    varHandle = getvariablehandles(names, url, netID, port)


    #Returns 0 if an error was encountered while requesting the variable handle
    if varHandle==0:
        return(0)


    numberOfVariables=len(writeRequest)

    #Define ReadWrite request's indexGroup for Reading values from PLC
    indexGroup=61569
    indexOffset=1*numberOfVariables

    #Use helper varbyte(x) to get the variable size from the
    varByteSize= [varbyte(x) for x in vartypes]

    #Extract the flat list of index offsets
    indexOffsetBytesFlat=varHandle[(-4*numberOfVariables):]

    #Split flat list of index offset in subgroup of 4, associated with each variables
    indexOffsetBytes=[indexOffsetBytesFlat[x:x+4] for x in range(0, len(indexOffsetBytesFlat), 4)]

    #Define the header
    writeQueryHeader= [[5, 240, 0, 0, indexOffsetBytes[x], varByteSize[x], 0, 0, 0] for x in range(numberOfVariables)]

    #Define the write request bytes
    writeQueryTail=[valueToByteArray(newValues[x] ,vartypes[x]) for x in range(numberOfVariables)]

    writeQuery=flatten(writeQueryHeader+writeQueryTail)


    base64EncodedQuery = base64.b64encode(bytearray(writeQuery)).decode('ascii')
    cbrLen=4*numberOfVariables+sum(varByteSize)


    headers = {'content-type': 'text/xml'}
    body = """<?xml version="1.0" encoding="UTF-8"?>
             <SOAP-ENV:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance/" xmlns:xsd="http://www.w3.org/2001/XMLSchema/"
                xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                <SOAP-ENV:Body><q1:ReadWrite xmlns:q1="http://beckhoff.org/message/">
          <netId xsi:type="xsd:string">"""+netID+"""</netId>
          <nPort xsi:type="xsd:int">"""+str(port)+"""</nPort><indexGroup xsi:type="xsd:unsignedInt">"""+str(indexGroup)+"""</indexGroup><indexOffset xsi:type="xsd:unsignedInt">"""+str(indexOffset)+"""</indexOffset>" +
            <cbRdLen xsi:type="xsd:int">"""+str(cbrLen)+"""</cbRdLen><pwrData xsi:type="xsd:base64Binary">"""+base64EncodedQuery+"""</pwrData>"
          </q1:ReadWrite></SOAP-ENV:Body></SOAP-ENV:Envelope>"""

    response = requests.post(url,data=body,headers=headers)
    tree = ET.ElementTree(ET.fromstring(response.content.decode('ascii')))

    root = tree.getroot()

    #Check for error code and return it if one is found
    errorcode=root.find('.//{http://beckhoff.org}errorcode')
    if errorcode!=None:
        errorNo=root.find('.//{http://beckhoff.org}errorcode').text
        print("TwinCAT error "+errorNo+ " encountered while retrieving handles: " +errorCode(int(errorNo)))
        return(0)
    else:
        return(newValues)


def errorCode(x):
    return {
        1 : "Internal error",
        2 : "No Rtime",
        3 : "Allocation locked memory error",
        4 : "Insert mailbox error",
        5 : "Wrong receive HMSG",
        6 : "target port not found",
        7 : "target machine not found",
        8 : "Unknown command ID",
        9 : "Bad task ID",
        10: "No IO",
        11: "Unknown AMS command",
        12: "Win 32 error",
        13: "Port not connected",
        14: "Invalid AMS length",
        15: "Invalid AMS Net ID",
        16: "Low Installation level",
        17: "No debug available",
        18: "Port disabled",
        19: "Port already connected",
        20: "AMS Sync Win32 error",
        21: "AMS Sync Timeout",
        22: "AMS Sync AMS error",
        23: "AMS Sync no index map",
        24: "Invalid AMS port",
        25: "No memory",
        26: "TCP send error",
        27: "Host unreachable",
        1792: "error class <device error>",
        1793: "Service is not supported by server",
        1794: "invalid index group",
        1795: "invalid index offset",
        1796: "reading/writing not permitted",
        1797: "parameter size not correct",
        1798: "invalid parameter value(s)",
        1799: "device is not in a ready state",
        1800: "device is busy",
        1801: "invalid context (must be in Windows)",
        1802: "out of memory",
        1803: "invalid parameter value(s)",
        1804: "not found (files, ...)",
        1805: "syntax error in command or file",
        1806: "objects do not match",
        1807: "object already exists",
        1808: "symbol not found",
        1809: "symbol version invalid",
        1810: "server is in invalid state",
        1811: "AdsTransMode not supported",
        1812: "Notification handle is invalid",
        1813: "Notification client not registered",
        1814: "no more notification handles",
        1815: "size for watch too big",
        1816: "device not initialized",
        1817: "device has a timeout",
        1818: "query interface failed",
        1819: "wrong interface required",
        1820: "class ID is invalid",
        1821: "object ID is invalid",
        1822: "request is pending",
        1823: "request is aborted",
        1824: "signal warning",
        1825: "invalid array index",
        1826: "symbol not active -> release handle and try again",
        1827: "access denied",
        1856: "Error class <client error>",
        1857: "invalid parameter at service",
        1858: "polling list is empty",
        1859: "var connection already in use",
        1860: "invoke ID in use",
        1861: "timeout elapsed",
        1862: "error in win32 subsystem",
        1863: "Invalid client timeout value",
        1864: "ads-port not opened",
        1872: "internal error in ads sync",
        1873: "hash table overflow",
        1874: "key not found in hash",
        1875: "no more symbols in cache",
        1876: "invalid response received",
        1877: "sync port is locked"
    }[x]


#Define variable size (in bytes) for each variables in the request
def varbyte(x):
    return{
        'INT': 2,
        'DINT': 4,
        'BOOL': 1,
        'REAL': 4,
        'LREAL': 8,
        'STRING': 80
    }[x]


#Define variable size (in bytes) for each variables in the request
def byteArrayToValue(myByte, myType):
    if myType =='INT':
        return(int.from_bytes(myByte, byteorder='big', signed=False))
    elif myType =='DINT':
        return(int.from_bytes(myByte, byteorder='big', signed=False))
    elif myType =='BOOL':
        intValue=int.from_bytes(myByte, byteorder='big', signed=False)
        if intValue==1:
            return(True)
        else:
            return(False)
    elif myType =='LREAL':
        return(struct.unpack('!d', myByte)[0])
    elif myType =='REAL':
        return(struct.unpack('!f', myByte)[0])
    elif myType =='STRING':
        rawString=myByte.decode('utf-8',"ignore")[::-1]
        trimmedString=rawString.split("\x00",1)[0]
        return(trimmedString)

#Define variable size (in bytes) for each variables in the request
def valueToByteArray(myValue, myType):
    if myType =='INT':
        return(list(myValue.to_bytes(2, byteorder='big'))[::-1])
    elif myType =='DINT':
        return(list(myValue.to_bytes(4, byteorder='big'))[::-1])
    elif myType =='BOOL':
        if myValue:
            return([1])
        else:
            return([0])
    elif myType =='LREAL':
        return(list(struct.pack('!d', myValue)[::-1]))
    elif myType =='REAL':
        return(list(struct.pack('!f', myValue)[::-1]))
    elif myType =='STRING':
        #String converted to ascii code
        charBytes=[ord(char) for char in myValue]
        #List padded to 80 bytes with zeros
        charBytes.extend([0]*(80-len(charBytes)))
        return(charBytes)



#Function to flatten lists
def flatten(items, seqtypes=(list, tuple)):
    for i, x in enumerate(items):
        while i < len(items) and isinstance(items[i], seqtypes):
            items[i:i+1] = items[i]
    return items
