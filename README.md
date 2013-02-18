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