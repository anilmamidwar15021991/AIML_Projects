import os
import sys;sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from sharepoint_service import sharepoint_restapi,sp_model,sharepoint_connect,sharepoint_connect_New,sharepoint_restapi_New



from dotenv import dotenv_values

import aiohttp
import asyncio
import requests
from typing import Type, Optional,TypeVar,Generic


base_dir=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
env_config=dotenv_values(os.path.join(base_dir,'config\.env'))

class SharepointConnector:

    def __init__(self,site_url,app_id,app_secret,base_url,token_url):
        self.app_id=app_id
        self.app_secret=app_secret
        self.site_url=site_url
        self.base_url=base_url
        self.token_url=token_url
        


    async def get_drive_id(self,auth_token):
        try:


            payload={'Content-Type':'application/json',
                            'Authorization':f"Bearer {auth_token}"

                    }
            endpoint=f"{self.base_url}/sites/{env_config['site_relative_path']}:/lists/{env_config['drive_name']}/drive"
            drive_response_model=sp_model.DriveResponseSchema('','')
            
            drive_id= (await sharepoint_restapi_New.get_endpoint(self,endpoint,auth_token,payload,response_model=drive_response_model)).id
            return drive_id
        except Exception as e:
            print(f"{e}")
    

        
        


    async def get_sp_files(sp,auth_token):
        '''
        retrieve all files from sharepoint 
        '''
        try:
                        
            drive_id= await sp.get_drive_id(auth_token)
            
            #get all items(files,folders) from document library - Policy '

            endpoint=f"{sp.base_url}/sites/{env_config['site_relative_path']}:/lists/Documents/items"
            #splist_response_model=sp_model.FileObject([]) #creating dataclass object
            splist_response_model=sp_model.FileObject('',[])
            payload={'Content-Type':'application/json',
                            'Authorization':f"Bearer {auth_token}"

                    }
            #items_list= await sharepoint_restapi_New.get_endpoint(sp,endpoint,auth_token,payload,response_model=splist_response_model)  #total listitems in doc library
            #splist_response_model= await sharepoint_restapi_New.get_endpoint(sp,endpoint,auth_token,payload,response_model=splist_response_model)
            items_list=sp_model.SPListItemsResponse()
            while True:
                splist_response_model= await sharepoint_restapi_New.get_endpoint(sp,endpoint,auth_token,payload,response_model=splist_response_model)
                if not splist_response_model.next_pagelink:
                    break
                items_list.append(splist_response_model.value)
                endpoint=splist_response_model.next_pagelink

            items_list=splist_response_model.value
            print(f"total no of items in {env_config['drive_name']} are {items_list.count_items()}")
            
            if items_list.count_items()>0:
                #get only files and skip folders
                document_list= [item for item in items_list.value if item.type=='Document']
                return document_list
            else:
                print("f no fileobjects present in document library")
                return None
            

        except Exception as e:
            print(f"Unable to retrieve the sharepoint files{e}")


    
    async def get_file_content(sp,auth_token,relative_path,file_type):

        try:

            drive_id= await sp.get_drive_id(auth_token)
            if file_type=='pdf':
                endpoint=f"{sp.base_url}/drives/{drive_id}/root:{relative_path}:/content"
                # payload={'Content-Type':'application/json',
                #          'Authorization':f"Bearer {auth_token}" }
                
                payload={'Content-Type':'application/pdf',
                    'Authorization':f"Bearer {auth_token}"}
                return await sharepoint_restapi_New.get_endpoint(sp,endpoint,auth_token,payload,str)
            else:
               
               print(f"Invalid document type")
        except Exception as e:
            print(f"Unable to read the content of file- {relative_path}")
    

# if __name__=="__main__":
#      asyncio.run(get_sp_files())