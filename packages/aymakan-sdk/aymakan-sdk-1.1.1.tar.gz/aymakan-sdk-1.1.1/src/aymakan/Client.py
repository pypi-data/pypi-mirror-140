import json
import requests


class Client:
    """
    A Client class to communicate with AyMakan API.
    ...

    Attributes
    ----------
    __url : str
        The API full url
    __api_key : str
        The customer secret key
    __testing : boolean
        To Set/Unset The current working environment

    Methods
    -------
    setApiKey(token):
        Takes in token and sets it.

    getApiKey():
        Returns the api token.

    setSandBox():
        Sets the current api url to development url.

    unsetSandBox():
        Sets the current api url to production url.

    isSandBox():
        To check the current working environment.
        
    prettyPrint(res):
        To print an indented/prettified version of JSON.
        

    for the other methods please visit https://github.com/aymakan/python-sdk/
    """
    __url = "https://api.aymakan.net/v2/"
    __api_key = ""
    __testing = False

    def __init__(self, url=None, api_key=None, testing=None):
        """
        Constructs all the necessary attributes for the client object.

        Parameters
        ----------
        url : str
            The API full url
        api_key : str
            The customer secret key
        testing : boolean
            To Set/Unset The current working environment
        """
        if url:
            self.__url = url
        if api_key:
            self.__api_key = api_key
        if testing:
            self.__testing = testing

    def setApiKey(self, token):
        """Takes in token and sets it."""
        self.__api_key = token

    def getApiKey(self):
        """Returns the api token."""
        return self.__api_key

    def setSandBox(self):
        """Sets the current api url to development url."""
        self.__testing = True
        self.__url = "https://dev-api.aymakan.com.sa/v2"

    def unsetSandBox(self):
        """Sets the current api url to production url."""
        self.__testing = False
        self.__url = "https://api.aymakan.net/v2"

    def isSandBox(self):
        """To check the current working environment."""
        return self.__testing

    def prettyPrint(self, res):
        """To print an indented/prettified version of JSON."""
        res = res.json()
        print(json.dumps(res, indent=4, sort_keys=True, ensure_ascii=False))

    def __callAPI(self, method, url=None, data=False):
        """
        The api caller method.

        Parameters
        ----------
        method : str
            The HTTP calling method
        url : str
            The specified api endpoint
        data : str, dict
            The required request data for the endpoint
        """

        headers = {
            'Accept': 'application/json',
            'Authorization': self.__api_key
        }

        ssl_verify = True
        timeout = 100

        try:
            if method == 'GET':
                r = requests.get(url, headers=headers, verify=ssl_verify, timeout=timeout)
            elif method == 'POST':
                r = requests.post(url, json=data, headers=headers, verify=ssl_verify, timeout=timeout)
            elif method == 'PUT':
                r = requests.put(url, json=data, headers=headers, verify=ssl_verify, timeout=timeout)
            else:
                r = requests.delete(url, json=data, headers=headers, verify=ssl_verify, timeout=timeout)

            return r

        except Exception as e:
            print(e)

    # General API methods

    def pingApi(self):
        return self.__callAPI('GET', self.__url + '/ping')

    def getCityList(self):
        return self.__callAPI('GET', self.__url + '/cities')

    def createShipment(self, data):
        return self.__callAPI('POST', self.__url + '/shipping/create', data)

    def createReversePickupShipment(self, data):
        return self.__callAPI('POST', self.__url + '/shipping/create/reverse_pickup', data)

    def trackShipment(self, tracking):
        if isinstance(tracking, list):
            tracking = ",".join(tracking)
        return self.__callAPI('GET', self.__url + '/shipping/track/' + tracking)

    def shipmentByReference(self, reference):
        if isinstance(reference, list):
            reference = ",".join(reference)
        return self.__callAPI('GET', self.__url + '/shipping/by_reference/' + reference)

    def cancelShipment(self, data):
        return self.__callAPI('POST', self.__url + '/shipping/cancel', data)

    def cancelShipmentByReference(self, data):
        return self.__callAPI('POST', self.__url + '/shipping/cancel_by_reference', data)

    def getShipmentLabel(self, tracking):
        return self.__callAPI('GET', self.__url + '/shipping/awb/tracking/' + tracking)

    def getBulkShipmentLabel(self, tracking):
        if isinstance(tracking, list):
            tracking = ",".join(tracking)
        return self.__callAPI('GET', self.__url + '/shipping/bulk_awb/trackings/' + tracking)

    def getCustomerShipments(self):
        return self.__callAPI('GET', self.__url + '/customer/shipments')

    # Pickup requests methods:

    def pickupRequest(self):
        return self.__callAPI('GET', self.__url + '/pickup_request/list')

    def createPickupRequest(self, data):
        return self.__callAPI('POST', self.__url + '/pickup_request/create', data)

    def cancelPickupRequest(self, data):
        return self.__callAPI('POST', self.__url + '/pickup_request/cancel', data)

    def timeSlots(self, data):
        return self.__callAPI('GET', self.__url + '/time_slots/' + data)

    # Customer address methods:

    def getAddress(self):
        return self.__callAPI('GET', self.__url + '/address/list')

    def createAddress(self, data):
        return self.__callAPI('POST', self.__url + '/address/create', data)

    def updateAddress(self, data):
        return self.__callAPI('PUT', self.__url + '/address/update', data)

    def deleteAddress(self, data):
        return self.__callAPI('DELETE', self.__url + '/address/delete', data)

    # WebHook API methods:

    def getWebHook(self):
        return self.__callAPI('GET', self.__url + '/webhooks/list')

    def createWebHook(self, data):
        return self.__callAPI('POST', self.__url + '/webhooks/create', data)

    def updateWebHook(self, data):
        return self.__callAPI('PUT', self.__url + '/webhooks/update', data)

    def deleteWebHook(self):
        return self.__callAPI('DELETE', self.__url + '/webhooks/delete')
