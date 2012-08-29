from google.appengine.api import memcache
from google.appengine.api import apiproxy_stub_map

class UserRPCTag(apiproxy_stub_map.UserRPC):
  def test_value_for_tags(self, value):
    return type(value) == dict and type(value.get('tags')) == dict and 'value' in value

  def get_result(self):
    result = super(UserRPCTag, self).get_result()

    all_tags = []
    result_with_tags = []
    for key, value in result.items():
      if self.test_value_for_tags(value):
        all_tags.extend(value['tags'])
        result_with_tags.append(key)

    if all_tags:
      versions = get_tags_versions(all_tags)

      for key in result_with_tags:
        value = result[key]
        for tag, version in value['tags'].items():
          if version != versions[tag]:
            result[key] = None
            break
        else:
          result[key] = value['value']

    return result

def create_rpc(deadline=None, callback=None):
  return UserRPCTag('memcache', deadline, callback)

class ClientTags(memcache.Client):
  def get_with_tags(self, key, key_prefix='', namespace=None, for_cas=False):
    return self.get_multi_with_tags([key], key_prefix, namespace, for_cas).get(key)

  def get_multi_with_tags(self, keys, key_prefix='', namespace=None, for_cas=False):
    rpc = self.get_multi_async_with_tags(keys, key_prefix, namespace, for_cas)
    return rpc.get_result()

  def get_multi_async_with_tags(self, keys, key_prefix='', namespace=None, for_cas=False, rpc=None):
    return self.get_multi_async(keys, key_prefix, namespace, for_cas, rpc)

  def set_multi_with_tags(self, mapping, tags, time=0, key_prefix='',
                                min_compress_len=0, namespace=None, rpc=None):
    rpc = self.set_multi_async_with_tags(mapping, tags, time, key_prefix, min_compress_len, namespace)
    return rpc.get_result()

  def set_with_tags(self, key, value, tags, time=0, key_prefix='',
                    min_compress_len=0, namespace=None,):
    return self.set_multi_with_tags({key:value}, tags, time, key_prefix, min_compress_len, namespace).get(key)

  def set_multi_async_with_tags(self, mapping, tags, time=0,  key_prefix='',
                                min_compress_len=0, namespace=None, rpc=None):

    tags_versions = get_tags_versions(tags)

    for key, value in mapping.items():
      value = {
        'tags': tags_versions,
        'value': value,
      }
      mapping[key] = value

    return self.set_multi_async(mapping, time, key_prefix=key_prefix,
                                min_compress_len=min_compress_len, namespace=namespace, rpc=rpc)

  def _make_async_call(self, rpc, method, request, response,
                       get_result_hook, user_data):
    if method.lower() == 'get':
      if rpc is None:
        rpc = create_rpc()

      if not isinstance(rpc, UserRPCTag):
        raise Exception('Bad rpc class. User memcache_tag.create_rpc()')

    return super(ClientTags, self)._make_async_call(rpc, method, request, response, get_result_hook, user_data)

  TAG_NAMESPACE = 'versions'

  def get_tags_versions(self, tags):
    result = memcache.get_multi(tags, namespace=self.TAG_NAMESPACE)
    for tag in tags:
      version = result.get(tag)
      if version is None:
        result[tag] = 1

    return result

  def delete_tag(self, tag):
    return memcache.incr(tag, namespace=self.TAG_NAMESPACE, initial_value=1)

_CLIENTTAGS = None

def setup_client(client_obj):
  global _CLIENTTAGS
  var_dict = globals()

  _CLIENTTAGS = client_obj
  var_dict['get_multi_async_with_tags'] = _CLIENTTAGS.get_multi_async_with_tags
  var_dict['get_multi_with_tags'] = _CLIENTTAGS.get_multi_with_tags
  var_dict['get_with_tags'] = _CLIENTTAGS.get_with_tags

  var_dict['set_multi_async_with_tags'] = _CLIENTTAGS.set_multi_async_with_tags
  var_dict['set_multi_with_tags'] = _CLIENTTAGS.set_multi_with_tags
  var_dict['set_with_tags'] = _CLIENTTAGS.set_with_tags

  var_dict['delete_tag'] = _CLIENTTAGS.delete_tag
  var_dict['get_tags_versions'] = _CLIENTTAGS.get_tags_versions

setup_client(ClientTags())

__all__ = ['get_multi_async_with_tags', 'get_multi_with_tags', 'get_with_tags',
           'set_multi_async_with_tags', 'set_multi_with_tags', 'set_with_tags',
           'delete_tag', 'get_tags_versions', 'create_rpc']