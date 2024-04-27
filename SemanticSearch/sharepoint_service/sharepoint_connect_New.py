import os
import sys;sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from dotenv import dotenv_values
from sharepoint_service import sp_model,sharepoint_restapi_New
import aiohttp
import asyncio
import requests
import datetime
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
        
    '''    get list id of all list from the SP site, list can be a documentlibrary or anything else (root hoempage)
    '''

    async def get_lists(self,auth_token):
        try:
            payload={'Content-Type':'application/json',
                            'Authorization':f"Bearer {auth_token}"

                    }
            
            endpoint=f"{self.base_url}/sites/{env_config['site_relative_path']}:/lists"
            list_response=sp_model.SPListResponse(value=[])
            list_ids=await sharepoint_restapi_New.get_endpoint(self,endpoint,auth_token,payload,response_model=list_response)
            print(f"total no of list items in {env_config['site_relative_path']} are {list_ids.count_items()}")

            documenttype_listitem = [listitem for listitem in list_ids.value if listitem['template']=='documentLibrary']
            print(f"no of document libraries available are -{len(documenttype_listitem)}")
            return documenttype_listitem
                     
        
        except Exception as e:
            print(f"{e}")
    

    async def get_drive_id(self,auth_token,list_id):
        try:


            payload={'Content-Type':'application/json',
                            'Authorization':f"Bearer {auth_token}"

                    }
            #endpoint=f"{self.base_url}/sites/{env_config['site_relative_path']}:/lists/{env_config['drive_name']}/drive" -- endpoint to get drive using relative path
            endpoint=f"{self.base_url}/sites/{env_config['site_relative_path']}:/lists/{list_id}/drive"
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

            list_ids=await sp.get_lists(auth_token)
            total_sp_items=[]
            if len(list_ids)!=0:
                for listid in list_ids:
                    #get drive id for each list_id
                    drive_id= await sp.get_drive_id(auth_token,listid['id'])
                    # endpoint to get all items in the list
                    endpoint=f"{sp.base_url}/sites/{env_config['site_relative_path']}:/lists/{listid['id']}/items"

                    splist_response_model=sp_model.FileObject('',[])
                    payload={'Content-Type':'application/json',
                            'Authorization':f"Bearer {auth_token}"

                    }
                    list_items_for_pages=[]
                    while True:
                        '''
                        looping through page of results, each page result have only 200 
                        '''
                        splist_response_model= await sharepoint_restapi_New.get_endpoint(sp,endpoint,auth_token,payload,response_model=splist_response_model)
                        list_items_for_pages.extend(splist_response_model.value)
                        for items in list_items_for_pages:
                            items.drive_id=drive_id
                        if splist_response_model.next_pagelink is None:
                            break                       
                        
                        endpoint=splist_response_model.next_pagelink
                    total_sp_items.extend(list_items_for_pages)
                print(f"total no of items in {env_config['drive_name']} are {len(total_sp_items)}")                
                if len(total_sp_items)>0:
                    #get only files and skip folders
                    document_list= [item for item in total_sp_items if item.type=='Document']
                    print(f"total no of SP items  of type document are  {len(document_list)}") 
                    return document_list
                else:
                    print("f no fileobjects present in document library")
                    return None                   
            else:
                raise ValueError("There are no documentLibraries available")           
            
            # #get all items(files,folders) from document library - Policy '

            # endpoint=f"{sp.base_url}/sites/{env_config['site_relative_path']}:/lists/list/items"
            
            # splist_response_model=sp_model.FileObject('',[])
            # payload={'Content-Type':'application/json',
            #                 'Authorization':f"Bearer {auth_token}"

            #         }
            # #items_list= await sharepoint_restapi_New.get_endpoint(sp,endpoint,auth_token,payload,response_model=splist_response_model)  #total listitems in doc library
            # #splist_response_model= await sharepoint_restapi_New.get_endpoint(sp,endpoint,auth_token,payload,response_model=splist_response_model)
            
            # items_list=[]

            # while True:
            #     '''
            #     looping through page of results, each page result have only 200 
            #     '''
            #     splist_response_model= await sharepoint_restapi_New.get_endpoint(sp,endpoint,auth_token,payload,response_model=splist_response_model)
            #     if not splist_response_model.next_pagelink:
            #         break
            #     items_list.extend(splist_response_model.value)
            #     #items_list=items_list.append(splist_response_model.value)
            #     endpoint=splist_response_model.next_pagelink

            
            # print(f"total no of items in {env_config['drive_name']} are {len(items_list)}")
            
            # if len(items_list)>0:
            #     #get only files and skip folders
            #     document_list= [item for item in items_list if item.type=='Document']
            #     return document_list
            # else:
            #     print("f no fileobjects present in document library")
            #     return None
            

        except Exception as e:
            print(f"Unable to retrieve the sharepoint files{e}")




    '''
    get file content of file by their type 
    '''
    async def get_file_content(sp,auth_token,drive_id,item_id,file_type):

        try:

            
            if file_type=='pdf':
                #endpoint=f"{sp.base_url}/drives/{drive_id}/root:{relative_path}:/content" - endpoint to get content using relative path
                endpoint=f"{sp.base_url}/drives/{drive_id}/items/{item_id}/content"
                
                payload={'Content-Type':'application/pdf',
                    'Authorization':f"Bearer {auth_token}"}
                return await sharepoint_restapi_New.get_endpoint(sp,endpoint,auth_token,payload,str)
                
            else:
               
               print(f"Invalid document type")
        except Exception as e:
            print(f"Unable to read the content of file- {item_id}")
    

