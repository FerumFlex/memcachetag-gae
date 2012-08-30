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
    rnd = random.randint(1, 1000000)
    self.assertEqual(memcachetag.set_with_tags('test', rnd, ['temp']), 1)
    self.assertEqual(memcachetag.get_with_tags('test'), rnd)

  def test_random(self):
    for i in range(1000):
      rnd = random.randint(1, 1000000)
      memcachetag.set_with_tags('test', rnd, ['temp'])
      self.assertEqual(memcachetag.get_with_tags('test'), rnd)

  def test_delete_tag(self):
    rnd = random.randint(1, 1000000)
    memcachetag.set_with_tags('test', rnd, ['temp'])
    self.assertEqual(memcachetag.get_with_tags('test'), rnd)

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
    version = memcachetag.delete_tag(random_tag)
    self.assertEqual(version, memcachetag.get_tags_versions([random_tag]).get(random_tag))

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
    rnd = random.randint(1, 1000000)
    rnd2 = random.randint(1, 1000000)

    res = memcachetag.set_multi_with_tags({'test': rnd, 'test2': rnd2}, ['temp'])
    self.assertEqual(len(res.keys()), 2)
    self.assertEqual(res.get('test'), 1)
    self.assertEqual(res.get('test2'), 1)

    res = memcachetag.get_multi_with_tags(['test', 'test2'])
    self.assertEqual(len(res.keys()), 2)
    self.assertEqual(res.get('test'), rnd)
    self.assertEqual(res.get('test2'), rnd2)

  def test_async(self):
    rnd = random.randint(1, 1000000)

    rpc = memcachetag.set_async_with_tags('test', rnd, ['temp'])
    self.assertEqual(rpc.get_result().get('test'), 1)

    rpc = memcachetag.get_async_with_tags('test')
    self.assertEqual(rpc.get_result().get('test'), rnd)


