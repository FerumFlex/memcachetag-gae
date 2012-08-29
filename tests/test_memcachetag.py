import unittest
import random
from google.appengine.ext import testbed
from google.appengine.api import memcache

import memcachetag

class MemcacheTagTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_memcache_stub()

  def tearDown(self):
    self.testbed.deactivate()

  def test_base(self):
    memcachetag.set_with_tags('test', 1, ['temp'])
    self.assertEqual(memcachetag.get_with_tags('test'), 1)

  def test_random(self):
    for i in range(1000):
      rnd = random.randint(1, 1000000)
      memcachetag.set_with_tags('test', rnd, ['temp'])
      self.assertEqual(memcachetag.get_with_tags('test'), rnd)

  def test_delete_tag(self):
    memcachetag.set_with_tags('test', 1, ['temp'])
    self.assertEqual(memcachetag.get_with_tags('test'), 1)

    memcachetag.delete_tag('temp')
    self.assertEqual(memcachetag.get_with_tags('test'), None)

  def test_tag_versions(self):
    tag = 'temp'
    version = memcachetag.get_tags_versions([tag]).get(tag)
    memcachetag.delete_tag(tag)
    self.assertEqual(version + 1, memcachetag.get_tags_versions([tag]).get(tag))

  def test_raise_rpc_error(self):
    rpc = memcache.create_rpc()
    with self.assertRaises(Exception):
      memcachetag.get_multi_async_with_tags(['test'], rpc=rpc)

  def test_many_sets_and_gets(self):
    data = {}
    for i in range(1000):
      key = "key" + str(i)
      value = random.randint(1, 100000)
      tag = "tag" + str(random.randint(1, 10))
      tags = [tag]
      data[key] = {
        'value': value,
        'tags': tags,
      }
      memcachetag.set_with_tags(key, value, tags)

    for key, d in data.items():
      value = d.get('value')
      self.assertEqual(memcachetag.get_with_tags(key), value)

    # delete random tag
    random_tag = "tag" + str(random.randint(1, 10))
    memcachetag.delete_tag(random_tag)

    for key, d in data.items():
      value = d.get('value')
      tags = d.get('tags')
      if random_tag in tags:
        self.assertEqual(memcachetag.get_with_tags(key), None)
      else:
        self.assertEqual(memcachetag.get_with_tags(key), value)

  def test_with_memcache(self):
    memcache.set('test', 'data')
    self.assertEqual(memcachetag.get_with_tags('test'), 'data')

  def test_multi(self):
    memcachetag.set_multi_with_tags({'test': 1, 'test2': 2}, ['temp'])
    res = memcachetag.get_multi_with_tags(['test', 'test2'])
    self.assertEqual(len(res.keys()), 2)
    self.assertEqual(res.get('test'), 1)
    self.assertEqual(res.get('test2'), 2)


