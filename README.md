Description
======================================================================

It is very simple and small library allows you to add tags to your memcache data. And invalidate only tag that you need.

How it works?
======================================================================

For each data it also saves the tags version. To invalidate that tag we should just increase version of the tag by one. So deleting the all data by tag has complexity O(1). But the data are not deleted and when you try get data it detects that version change and returns None. So each call to the get also has additionale request versions of the all data tags.

Example of use
======================================================================

Set with tag, get with tag, delete tag
----------------------------------------------------------------------

    import memcachetag

    memcachetag.set_with_tags('test', 1, ['temp'])
    print memcachetag.get_with_tags('test') # will print 1

    memcachetag.delete_tag('temp')
    print memcachetag.get_with_tags('test') # will print None


Using async
----------------------------------------------------------------------

    import memcachetag
    import random

    rnd = random.randint(1, 1000000)

    rpc = memcachetag.set_async_with_tags('test', rnd, ['temp'])
    print rpc.get_result().get('test') # will print 1 (success)

    rpc = memcachetag.get_async_with_tags('test') 
    print rpc.get_result().get('test') # will print rnd

Enjoy it :)
======================================================================
