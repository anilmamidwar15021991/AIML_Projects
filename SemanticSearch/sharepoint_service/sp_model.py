from dataclasses import dataclass,field
from datetime import datetime
from typing import List,Any, Type
from collections import defaultdict




@dataclass
class SPFolderResponse:
    pass


@dataclass
class FolderResponseSchema:
    '''
    dataclass to hold the response of SP folder get API
    #sample get uri ='https://graph.microsoft.com/v1.0/drives/{drive-id}/items/root/children'
    
    '''
    name:str
    item_count:int
    created_datetime:datetime
    unique_id:str
    child_foldercount:int
    last_modifiedtime:datetime

    @classmethod
    def parsed_json(cls,json_data):
        return cls(
            name=json_data.get('name'),
            item_count=json_data['folder']['childCount'],
            created_datetime=json_data.get('createdDateTime'),
            unique_id=json_data.get('id'),
            child_foldercount=json_data['folder']['childCount'],
            last_modifiedtime=json_data.get('lastModifiedDateTime')
                  
        )


@dataclass
class FolderRootObject():
    
    value:List[FolderResponseSchema]=field(default_factory=[])

    def __post_init__(self):
        #self.value=[FolderResponseSchema(**x) for x in self.value]
        self.value=[FolderResponseSchema.parsed_json(self.value)]


@dataclass
class DriveResponseSchema:
    name:str
    id:str

    @classmethod
    def from_json(cls,json_data):
        return cls(
            name=json_data.get('name'),
            id=json_data.get('id')
        )
    

@dataclass
class SPListItemsResponse:
    '''
    data class to hold the metadata valuye for drive items ,it could 
    be a folder, file(dcx,pdf,xlsx etc)
    '''
    web_url:str
    type:str
    site_id:str

    @classmethod
    def parsed_json(cls,json_data):
        return cls(
            web_url=json_data.get('webUrl'),
            type=json_data['contentType']['name'],
            site_id=json_data['parentReference']['siteId']
            )



@dataclass
class FileObject:
    next_pagelink:str
    value:List[SPListItemsResponse]=field(default_factory=[])
    '''
    data class to hold the values of all list items from
    document library (ex- files,folders, documents)
    '''
    # def __post_init__(self):
    #     self.value=[SPListItemsResponse.parsed_json(x) for x in self.value]
   
    def process(self):
        self.value=[SPListItemsResponse.parsed_json(x) for x in self.value]
        self.next_pagelink=self.next_pagelink
        
        

    @classmethod
    def from_json(cls,json_data):
        next_pagelink=json_data.get('@odata.nextLink')
        json_data= json_data.get('value',[])        
        value=[SPListItemsResponse.parsed_json(x) for x in json_data]
        return cls(next_pagelink,value)
        #return cls(value=[SPListItemsResponse.parsed_json(x) for x in json_data])

    
    def count_items(self) -> int:
        '''function to return the count of Fileobject items
        '''
        return len(self.value)
    
    def list_count(self) -> int:
        '''
        function to return the count of files 
        '''
        return len([item for item in self.value if item.type=='Document' ])
