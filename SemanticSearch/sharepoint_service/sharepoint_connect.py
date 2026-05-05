import os
import sys;sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from sharepoint_service import sharepoint_restapi,sp_model,sharepoint_connect



from dotenv import dotenv_values

import aiohttp
import asyncio
import requests
from typing import Type, Optional,TypeVar,Generic


base_dir=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
env_config=dotenv_values(os.path.join(base_dir,'config\.env'))




async def get_sp_files(sp,auth_token):
    '''
    retrieve all files from sharepoint 
    '''
    try:
        # sp=sharepoint_restapi.SharepointConnector(env_config['site_url'],
        #                                       env_config['App_Id'],
        #                                       env_config['App_Secret'],
        #                                       env_config['base_url'],
        #                                       env_config['Access_Tokenurl'])

        # auth_token= await sp.acquire_token()
        # print(auth_token)
        # retrieve all items from drive - shared documents drive
        payload={'Content-Type':'application/json',
                    'Authorization':f"Bearer {auth_token}"

            }
        endpoint=f"{sp.base_url}/sites/{env_config['site_relative_path']}:/lists/{env_config['drive_name']}/drive"
        drive_response_model=sp_model.DriveResponseSchema('','')
        drive_id= (await sp.get_endpoint(endpoint,auth_token,payload,response_model=drive_response_model)).id
        
        #get all items(files,folders) from document library - Policy '

        endpoint=f"{sp.base_url}/sites/{env_config['site_relative_path']}:/lists/Documents/items"
        splist_response_model=sp_model.FileObject([]) #creating dataclass object
        items_list= await sp.get_endpoint(endpoint,auth_token,payload,response_model=splist_response_model)  #total listitems in doc library
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
        drive_response_model=sp_model.DriveResponseSchema('','')
        endpoint=f"{sp.base_url}/sites/{env_config['site_relative_path']}:/lists/{env_config['drive_name']}/drive"
        drive_id= (await sp.get_endpoint(endpoint,auth_token,response_model=drive_response_model)).id
        if file_type=='pdf':
            endpoint=f"{sp.base_url}/drives/{drive_id}/root:{relative_path}:/content"
            return await sp.get_endpoint(endpoint,auth_token,str)
        else:
           print(f"Invalid document type")
    except Exception as e:
        print(f"Unable to read the content of file- {relative_path}")
    

if __name__=="__main__":
     asyncio.run(get_sp_files())