from algoliasearch_django import algolia_engine

from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register
from algoliasearch_django import raw_search


from .models import Course

def get_client():
    return algolia_engine.client

def get_index(index_name='Learnit'):
    client = get_client()
    index = client.init_index(index_name)
    return index

def perform_search(query, **kwargs):
    index = get_index()
    params = {}
    tags = ""
    if "tags" in kwargs:
        tags = kwargs.pop("tags") or []
        if len(tags) != 0:
            params['tagFilters'] = tags
    index_filters = [f"{k}:{v}" for k,v in kwargs.items() if v]
    if len(index_filters) != 0:
         params['facetFilters'] = index_filters
    results = index.search(query, params)
    return results


@register(Course)
class CourseIndex(AlgoliaIndex):
    fields = [
        'title',
        'thumbnail',
        'user',
        'price',
        'level',
    ]

    def get_model(self):
        return Course
#     settings = {
#         'searchableAttributes': ['title', 'level'],
#         'attributesForFaceting': ['user']
#     }
#     # tags = 'get_categories'


# params = { "hitsPerPage": 5 }
# response = raw_search(Course, "django", params)