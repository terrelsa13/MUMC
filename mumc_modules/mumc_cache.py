import inspect
import time
from sys import getsizeof


#Cached URL request controls
class cached_data_handler:
    #Initialize and define cache variables
    def __init__(self,cfg):
        self.cached_data={}
        self.cached_entry_urls=[]
        self.cached_entry_sizes=[]
        self.cached_entry_hits=[]
        self.cached_entry_times=[]
        self.cached_data_hits=0
        self.cached_data_misses=0
        self.total_cached_data_size=0
        self.total_data_size_thru_cache=0
        self.total_cached_data_size_removed=0
        self.newest_cached_data_entry_number=None
        self.oldest_cached_data_entry_number=None
        self.total_cumulative_cached_data_entry_number=None
        self.updateCacheVariables(cfg)


    #Upated defined cache variables
    def updateCacheVariables(self,cfg):
        try:
            self.api_query_cache_size=cfg['admin_settings']['cache']['size'] * cfg['bytes_in_megabytes']
        except:
            self.api_query_cache_size=cfg['cache_size'] * cfg['bytes_in_megabytes']
        try:
            self.api_query_cache_fallback_behavior=cfg['admin_settings']['cache']['fallback_behavior'].upper()
        except:
            self.api_query_cache_fallback_behavior=cfg['fallback_behavior']
        try:
            self.api_query_cache_minimum_age=cfg['admin_settings']['cache']['minimum_age']
        except:
            self.api_query_cache_minimum_age=cfg['minimum_age']


    def wipeCache(self):
        self.cached_data={}
        self.cached_entry_urls=[]
        self.cached_entry_sizes=[]
        self.cached_entry_hits=[]
        self.cached_entry_times=[]
        self.total_cached_data_size_removed+=self.total_cached_data_size
        self.total_cached_data_size=0
        self.newest_cached_data_entry_number=None
        self.oldest_cached_data_entry_number=None
        self.total_cumulative_cached_data_entry_number=None

    def checkURLInCache(self,url):
        if (url in self.cached_entry_urls):
            return True
        else:
            return False

    def getIndexFromURL(self,url):
        if (self.checkURLInCache(url)):
            return self.cached_entry_urls.index(url)
        else:
            return None

    def getCachedDataFromURL(self,url):
        try:
            if (self.checkURLInCache(url)):
                index=self.getIndexFromURL(url)
                self.cached_entry_hits[index]+=1
                self.cached_entry_times[index]=time.time()*1000
                self.cached_data_hits+=1
                return self.cached_data[url]
            else:
                self.cached_data_misses+=1
                return False
        except:
            return None

    #Recursively find size of data objects
    #Credit to https://github.com/bosswissam/pysize/blob/master/pysize.py
    def getDataSize(self,obj,seen=None):
        size = getsizeof(obj)
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        # Important mark as seen *before* entering recursion to gracefully handle
        # self-referential objects
        seen.add(obj_id)
        if hasattr(obj, '__dict__'):
            for cls in obj.__class__.__mro__:
                if '__dict__' in cls.__dict__:
                    d = cls.__dict__['__dict__']
                    if inspect.isgetsetdescriptor(d) or inspect.ismemberdescriptor(d):
                        size += self.getDataSize(obj.__dict__, seen)
                    break
        if isinstance(obj, dict):
            size += sum((self.getDataSize(v, seen) for v in obj.values()))
            size += sum((self.getDataSize(k, seen) for k in obj.keys()))
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            try:
                size += sum((self.getDataSize(i, seen) for i in obj))
            except TypeError:
                #logging.exception("Unable to get size of %r. This may lead to incorrect sizes. Please report this error.", obj)
                pass
        if hasattr(obj, '__slots__'): # can have __slots__ with __dict__
            size += sum(self.getDataSize(getattr(obj, s), seen) for s in obj.__slots__ if hasattr(obj, s))
            
        return size

    def removeCachedEntry(self,url):
        try:
            index=self.getIndexFromURL(url)
            size=self.cached_entry_sizes[index]
            self.cached_entry_sizes.pop(index)
            self.cached_entry_hits.pop(index)
            self.cached_entry_urls.pop(index)
            self.cached_entry_times.pop(index)
            self.cached_data.pop(url)
            self.total_cached_data_size-=size
            self.total_cached_data_size_removed+=size
            if (self.oldest_cached_data_entry_number == None):
                self.oldest_cached_data_entry_number=0
            else:
                self.oldest_cached_data_entry_number+=1
            return True
        except:
            return False


    def getLowestAttributeValueCacheEntryIndex(self,cached_data_list):
        return cached_data_list.index(min(cached_data_list))


    def getTimeWindow(self):
        return (time.time() * 1000) - self.api_query_cache_minimum_age


    def addEntryToCache(self,url,data):
        potentialEntrySize=(self.getDataSize(url) + self.getDataSize(data))
        if (potentialEntrySize <= self.api_query_cache_size):
            try:
                if (potentialEntrySize > (self.api_query_cache_size - self.total_cached_data_size)):
                    #LRU get time window
                    safety_time_window=self.getTimeWindow()
                    temp_cached_entry_hits=self.cached_entry_hits.copy()
                    temp_cached_entry_urls=self.cached_entry_urls.copy()
                    temp_cached_entry_times=self.cached_entry_times.copy()
                while potentialEntrySize > (self.api_query_cache_size - self.total_cached_data_size):
                    if (len(self.cached_entry_sizes) > 0):
                        #LFU get least accessed cache entry
                        least_accessed_entry_index=self.getLowestAttributeValueCacheEntryIndex(temp_cached_entry_hits)

                        #Verify entry is outside of the safety window
                        if (temp_cached_entry_times[least_accessed_entry_index] < safety_time_window):
                            self.removeCachedEntry(self.cached_entry_urls[self.getIndexFromURL(temp_cached_entry_urls[least_accessed_entry_index])])
                            temp_cached_entry_hits=self.cached_entry_hits.copy()
                            temp_cached_entry_urls=self.cached_entry_urls.copy()
                            temp_cached_entry_times=self.cached_entry_times.copy()
                        else:
                            temp_cached_entry_hits.pop(least_accessed_entry_index)
                            temp_cached_entry_urls.pop(least_accessed_entry_index)
                            temp_cached_entry_times.pop(least_accessed_entry_index)

                        if (len(temp_cached_entry_hits) == 0):
                            if (self.api_query_cache_fallback_behavior == 'FIFO'):
                                #FIFO Remove oldest cached entry
                                self.removeCachedEntry(self.cached_entry_urls[0])
                            elif (self.api_query_cache_fallback_behavior == 'LFU'):
                                #LFU Remove oldest and least accessed cache entry
                                self.removeCachedEntry(self.cached_entry_urls[self.getLowestAttributeValueCacheEntryIndex(self.cached_entry_hits)])
                            else: #(self.api_query_cache_fallback_behavior == 'LRU'):
                                #LRU Remove cache entry with oldest access time
                                self.removeCachedEntry(self.cached_entry_urls[self.getLowestAttributeValueCacheEntryIndex(self.cached_entry_times)])
                            temp_cached_entry_hits=self.cached_entry_hits.copy()
                            temp_cached_entry_urls=self.cached_entry_urls.copy()
                            temp_cached_entry_times=self.cached_entry_times.copy()
                    else:
                        self.wipeCache()
                self.cached_data[url]=data
                self.cached_entry_times.append(time.time() * 1000)
                self.cached_entry_urls.append(url)
                self.cached_entry_hits.append(0)
                self.cached_entry_sizes.append(potentialEntrySize)
                size=self.cached_entry_sizes[self.getIndexFromURL(url)]
                self.total_cached_data_size+=size
                self.total_data_size_thru_cache+=size
                if (self.newest_cached_data_entry_number == None):
                    self.newest_cached_data_entry_number=0
                else:
                    self.newest_cached_data_entry_number+=1
                if (self.oldest_cached_data_entry_number == None):
                    self.oldest_cached_data_entry_number=0
                if (self.total_cumulative_cached_data_entry_number == None):
                    self.total_cumulative_cached_data_entry_number=1
                else:
                    self.total_cumulative_cached_data_entry_number+=1
                return True
            except:
                return False
        else:
            return False


    def getCachedEntrySize(self,url):
        try:
            return self.cached_entry_sizes[self.getIndexFromURL(url)]
        except:
            return None


    def getCachedEntryHits(self,url):
        try:
            return self.cached_entry_hits[self.getIndexFromURL(url)]
        except:
            return None


    def getCachedEntryTime(self,url):
        try:
            return self.cached_entry_times[self.getIndexFromURL(url)]
        except:
            return None