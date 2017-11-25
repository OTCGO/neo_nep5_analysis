from django.core.cache import cache

class Cache(object):
    def __init__(self):
        self.cache = cache

    def get_height(self):
        return self.cache.get('height')

    def set(self,key,value,timeout=150):
        print '-'*10,key
        print '-'*10,value
        self.cache.set(key,value)
        print cache.get(key)
        print id(cache)

    def get(self,key):
        self.cache.get(key)
        print id(cache)
