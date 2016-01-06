The script crawls the twitter friend graph, and finds links of the type
a->b->c->a, which means that triplets (a,b,c) such that 'a' is a friend of 'b',
'b' is a friend of 'c', and 'c' is a friend of 'a'. Uses map-reduce for fast
computation.
