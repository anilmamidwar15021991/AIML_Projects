
import os
import sys;sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from dotenv import dotenv_values

import aiohttp
import asyncio
import requests
from typing import Type, Optional,TypeVar,Generic
from sharepoint_service.sp_model import FolderRootObject,DriveResponseSchema,FileObject
from requests_ntlm import HttpNtlmAuth
from O365 import Account, MSGraphProtocol,MSOffice365Protocol ,connection
import os
from office365.runtime.auth.token_response import TokenResponse
from office365.graph_client import GraphClient
import msal




base_dir=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
#env_config=dotenv_values(os.path.join(base_dir,'config\.env'))

        
async def acquire_token(self):
        #method to get bearer token -WORKING
        try:

            authority_url = self.token_url
            app = msal.ConfidentialClientApplication(
                authority=authority_url, client_id=self.app_id,client_credential=self.app_secret
            )

            token_json = app.acquire_token_for_client(
                            scopes=["https://graph.microsoft.com/.default "]
            )
            #logging goes here'
            if 'access_token' in token_json:
                return token_json['access_token']
            else:
                return token_json.get('error')
        except Exception as e:
            print(f"Unable to retrieve token{e}")
            raise Exception (f"Unable to retrieve token{e}")
        
T=TypeVar('T')
async def get_endpoint(self,request_url: str,auth_token: str,payload:dict[str,any], response_model: Optional [T]=None) -> Optional [T]:
        
        
        """returns API  response to a list fo dataclass

        Args:
            request_url (str): https://graph.microrosoft.com/v1.0
            auth_token (str): bearer token

        Returns:
            List: of dataclass 
        """
        # payload={'Content-Type':'application/json',
        #             'Authorization':f"Bearer {auth_token}"

        #     }
        try:
            #result=response_model()
            print(payload)
            print(type(response_model))
            print(response_model)
            async with aiohttp.ClientSession(headers=payload) as session:
                async with session.get(request_url) as response:
                     
                    response.raise_for_status()
                    if  payload['Content-Type']=='application/json':
                         json_data=await response.json() 
                         
                    else:
                         pdf_data= await response.content.read()                         
                    
                    result= response_model.from_json(json_data)
                    print(result)
                     
        except Exception as  e:
            #logging goes here
            print(f"Get request error {e}")
            raise
        return result
    
    




   


