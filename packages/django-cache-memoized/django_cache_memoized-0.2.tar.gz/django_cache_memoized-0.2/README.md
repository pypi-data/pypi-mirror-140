# Django Cache Memoized

[Django](https://www.djangoproject.com/) is one of the most popular Python web frameworks today. Importantly it provides an [ORM](https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping) permitting us to define models as Python classes that Django maps to a database representation for us. 

it supports a [configurable Caching system](https://docs.djangoproject.com/en/4.0/topics/cache/) as well to boost performance significantly (rendering pages from cache rather than rebuilding them from database queries).

Alas it does not provide easy access to the arbitrary [memoization](https://en.wikipedia.org/wiki/Memoization) of functions and methods using that cache. And while it does provide a [cached_property](https://docs.djangoproject.com/en/4.0/ref/utils/#django.utils.functional.cached_property) decorator, it implements that using a dictionary which has the lifetime of a request typically and it only applies to methods.

Here we provide a new decorator which will decorate an arbitrary function or method, and with which you can specify a caching key.

## Memoization and Cache keys
A brief introduction is warranted. To memoize a function  means to cache the result that it returns and on subsequent calls to that function with the same arguments, rather than *recalculate*, the result, return the previously cached result.

These results are stored in a cache with an key that can be used to retied the result later from the same cache. The key must identify the function and its arguments uniquely, and be unique to this function and the arguments it was called with, for the cached result to be of any use. 

While keys can be generated automatically to try and achieve that,  Django Cache Memoized aloows you to define one flexibly as well.

## How to use

Firstly, configure [Django caching](https://docs.djangoproject.com/en/4.0/topics/cache/). Without caching configured it makes no sense to memoize function to the cache.

Once configured you can memoize any function or method as follows. Three styles are supported:

```python
from django_cache_memoized import memoized

@memoized
def my_function(arg1, arg2 ...)
    ...
    return result
```

This will cache `result` against a default key, which is generated from the name of the function,  the class (if it is a method) and the arguments it was called with.

```python
from django_cache_memoized import memoized

@memoized()
def my_function(arg1, arg2 ...)
    ...
    return result
```

The same deal really. Just has optional and meaningless parentheses is all.

```
from django-cache-memoized import memoized

@memoized("a key pattern")
def my_function(arg1, arg2 ...)
    ...
    return result
```

That is with a key pattern specified. The pattern is simply an [f-string](https://docs.python.org/3/reference/lexical_analysis.html#formatted-string-literals), crucially without the **f** prefix. It can reference any of the arguments of the to-be-memoized function. For example a sample key pattern for the sample function above might be `"my_function({arg1}, {arg2})"`.

The f-string will be evaluated inside the decorated function when with the actually values of arg1 and arg2 etc that the function was called with.

Finally, if the first argument is named 'self' then the function assumed to be a class method. If it has an attribute 'pk' (for primary key) it is further assumed to be a method on a Django model instance. 

But you can force it to treat the function as a method with one optional argument:

```
from django_cache_memoized import memoized

@memoized("a key pattern", method=True)
def my_function(arg1, arg2 ...)
    ...
    return result
```

To be honest all that does, is impact the default key generator used. That is all really.

## Performance boost

I wrote this because of particular need. A Django view that presented summary data to which I added drill down using a [`<details>`](https://www.w3schools.com/TAGS/tag_details.asp) tag. The details though were easiest to generate by querying the relevant models. Doing that in the template once per row in a table had a fairly hefty impact on load time. My one page was generating 4000 queries on load. One hefty table!

So I was faced with some serious head scratching query generation, joining a pile of tables and aggregating lists somehow (some of which I did do) and/or memoizing ... And many of those 4000 queries were repeats, certainly on revisits tot he page but even within the page. 

And I simply could not find a flexible memoizer of any kind let alone one that used the configured Django cache. So I wrote one.

That one page had a load time of about 7 seconds (and about 3000 queries) before memoization and with first cut memoization (i.e. just one one bottle-necked template tag I have) it dropped to under 0.7 seconds (and 7 queries). Still too many but I wanted to illustrate just how eye-opening the first `@memoized` decoration's impact was. It only gets better.

## The catch

There's a catch of course. And one you will have to be aware of and manage. But this is true of all memoization. That is you need to be aware of the life cycle of the Django cache - it's different with different configurations but essentially cached items only live for so long, they typically expire at some point. That's not generally an issue unless it's too short and you're not getting a lot of benefit across requests and visits from the cache. The bigger problem to be aware of is the validity of the cached result. For example if you're caching model instance properties at all (and why not?! if it makes sense to) then if that model instance is edited and saved that might invalidate some of the cached results. Meaning you need to be aware when saving data to the data base that invalidating some cache entries is important. Failing to do so means pages using memoized results won't see the edits saved to the database.





