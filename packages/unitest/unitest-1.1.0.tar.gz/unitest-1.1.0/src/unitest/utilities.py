import json
import logging
import requests
from FunctionalTests.FunctionalParam import FunctionalParam
# from jsonpath_ng import jsonpath, parse

functionalParm = FunctionalParam()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

stagelink = "ifi/151613/"
endpoint = "https://plutus.mum1-stage.zeta.in/plutus-onboarding/send/otp"
file_name="endPointUserConf.json"

def get_stage():
    with open(file_name) as json_file:
        properties = json.load(json_file)
        env = properties["testingEndPoint"]["env"]
    print(env)
    return env


class Utilities(object):

    def __init__(self):
        pass

    def generate_token(self, phonenumber, otp, endpoint):
        endpoint = endpoint

        requests.request("GET", endpoint, headers=functionalParm.getHeader("defaultUser"))

    def check_status_code(self,
                          endPoint=None,
                          requestMethod="GET",
                          user="Captain_America",
                          params=None,
                          expectedStatusCode=requests.codes.ok,
                          jsonPayload=None):
        if user != 'null':
            headers = functionalParm.getHeader(user)
        else:
            headers = None

        if ((endPoint.find(stagelink) != -1) and (get_stage()=='beta')):
            endPoint = endPoint.replace("ifi/151613", "ifi/13")
        response = requests.request(requestMethod, endPoint, headers=headers, params=params, json=jsonPayload)
        logger.info(f"status code{response.status_code}")
        assert response.status_code == expectedStatusCode, \
            f"Expected Status Code {expectedStatusCode} and Actual status {response.status_code} code did not match"
        # logger.info(response.json())
        return response
        pass

    def check_user_authentication(self,
                                  endPoint,
                                  requestMethod="GET",
                                  user="DeadPool",
                                  params=None,
                                  expectedStatusCode=requests.codes.unauthorized,
                                  jsonPayload=None):
        if user != 'null':
            headers = functionalParm.getHeader(user)
        else:
            headers = None

        if ((endPoint.find(stagelink) != -1) and (get_stage()=='beta')):
            endPoint = endPoint.replace("ifi/151613", "ifi/13")
        response = requests.request(requestMethod, endPoint, headers=headers, params=params, json=jsonPayload)
        logger.info(f"status code{ response.status_code}")
        assert response.status_code == expectedStatusCode, \
            "Expected and Actual status code did not match"
        logger.info(response.json())
        return response
        pass

    def null_check(self, ):
        raise NotImplementedError("not implemented")

    def empty_check(self):
        raise NotImplementedError("not implemented")

    def schema_validation(self):
        raise NotImplementedError("not implemented")

    def db_validation(self):
        raise NotImplementedError("not implemented")
        
        
    def check_status_code_with_custom_header(self,
                          endPoint=None,
                          requestMethod="GET",
                          headers=None,
                          params=None,
                          expectedStatusCode=requests.codes.ok,
                          jsonPayload=None):

        if ((endPoint.find(stagelink) != -1) and (get_stage()=='beta')):
            endPoint = endPoint.replace("ifi/151613", "ifi/13")
        response = requests.request(requestMethod, endPoint, headers=headers, params=params, json=jsonPayload)
        logger.info(f"status code{response.status_code}")
        logger.info("--------CURL START---------")
        functionalParm.curl_request(response.request.url,requestMethod,headers,jsonPayload)
        logger.info("--------CURL END---------")
        assert response.status_code == expectedStatusCode, \
            f"Expected Status Code {expectedStatusCode} and Actual status {response.status_code} code did not match with failure reason {response.json()}"
        return response
        pass
