from mumc_modules.mumc_library_queries import get_all_libraries_from_media_server,get_all_library_subfolders


#user library class for builder
class user_library:

    def __init__(self,lib_id='',collection_type='',path='',network_path='',subfolder_id='',lib_enabled=False):
        self.lib_id=lib_id
        self.collection_type=collection_type
        self.path=path
        self.network_path=network_path
        self.subfolder_id=subfolder_id
        self.lib_enabled=lib_enabled

    def __str__(self):
        if (self.collection_type == 'movies'):
            strAlignment="-----"
        elif (self.collection_type == 'tvshows'):
            strAlignment="----"
        elif ((self.collection_type == 'music') or (self.collection_type == 'books')):
            strAlignment="------"
        else: #(self.collection_type == 'audiobooks')
            strAlignment="-"
            
        return f"{self.collection_type} {strAlignment} Path: {self.path} - NetPath: {self.network_path} - LibId: {self.lib_id} - SubFolderId: {self.subfolder_id}"


#media library class for builder
class media_library(user_library):

    def __init__(self,lib_id='',collection_type='',path='',network_path='',subfolder_id='',lib_enabled=False,name='',selected=False):
        user_library.__init__(self,lib_id,collection_type,path,network_path,subfolder_id,lib_enabled)
        self.name=name
        self.selected=selected

    def __str__(self):
        if (self.collection_type == 'movies'):
            strAlignment="-----"
        elif (self.collection_type == 'tvshows'):
            strAlignment="----"
        elif ((self.collection_type == 'music') or (self.collection_type == 'books')):
            strAlignment="------"
        else: #(self.collection_type == 'audiobooks')
            strAlignment="-"
            
        return f"{self.collection_type} {strAlignment} Name: {self.name} - Path: {self.path} - NetPath: {self.network_path} - LibId: {self.lib_id} - SubFolderId: {self.subfolder_id}"


def get_all_libraries(the_dict):
    allLibrariesList=[]
    isEmby=the_dict['isEmby']
    libraryId=the_dict['libraryId']

    #get all libraries from media server
    virtualFolders=get_all_libraries_from_media_server(the_dict)

    #loop thru libraries
    for virtFolder in virtualFolders:
        #filter library results by collection type
        if ((virtFolder['CollectionType'] == 'movies') or
            (virtFolder['CollectionType'] == 'tvshows') or
            (virtFolder['CollectionType'] == 'music') or
            (virtFolder['CollectionType'] == 'audiobooks') or
            (virtFolder['CollectionType'] == 'books')):
            #loop thru subfolder paths within this library
            for pathInfo in virtFolder['LibraryOptions']['PathInfos']:
                #when emby; the subfolders need to be specifically handled
                if (isEmby):
                    #query server for subfolder specific information
                    libraryInfoSubfolderInfo=get_all_library_subfolders(the_dict)
                    #loop thru returned library information
                    for libraryInfo in libraryInfoSubfolderInfo:
                        #check if subfolder's parent library id matches virtual folder's id
                        if (libraryInfo[libraryId] == virtFolder[libraryId]):
                            #loop thru subfolders for this library
                            for subfolderInfo in libraryInfo['SubFolders']:
                                #check if subfolder's path matches subfolder path of the virtual folder
                                if (subfolderInfo['Path'] == pathInfo['Path']):
                                    #try saving the network path
                                    try:
                                        networkPath=pathInfo['NetworkPath']
                                    except:
                                        networkPath=None
                                    #create list of library (sub)folder information objects
                                    allLibrariesList.append(media_library(lib_id=virtFolder[libraryId],collection_type=virtFolder['CollectionType'],path=pathInfo['Path'],network_path=networkPath,subfolder_id=subfolderInfo['Id'],name=virtFolder['Name']))
                            break
                #when jellyfin; subfolders do not exist and cannot be specifically handled
                else:
                    #try saving the network path
                    try:
                        networkPath=pathInfo['NetworkPath']
                    except:
                        networkPath=None
                    #create list of library folder information objects
                    allLibrariesList.append(media_library(id=virtFolder[libraryId],collectionType=virtFolder['CollectionType'],path=pathInfo['Path'],name=virtFolder['Name']))

    return allLibrariesList