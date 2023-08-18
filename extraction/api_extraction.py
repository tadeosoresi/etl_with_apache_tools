import os
from typing import Union
from typing import Iterator
import json
import requests

class TMDBApiData():
    """
    """
    movies_endpoint = "https://api.themoviedb.org/3/trending/movie/week?language=en-US&page={}"
    cast_endpoint = "https://api.themoviedb.org/3/movie/{}/credits?language=en-US"
    headers = {
            "accept": "application/json",
            "Authorization": "Bearer " + os.environ['TMDB_API_TOKEN']
        }

    @classmethod
    def get_data(cls) -> Iterator:
        """
        """
        page = 1
        while True:
            print(f'page {page}')
            url = cls.movies_endpoint.format(page)
            response = requests.get(url, headers=cls.headers)
            response = response.json()
            if response.get('success', None) == False: break
            results = response.get('results')
            for content in results:
                content_id = content['id']
                content['cast'] = cls.get_cast(content_id)
                yield content
    
    @classmethod
    def get_cast(cls, content_id:int) -> Union[None, dict]:
        """
        """
        url = cls.cast_endpoint.format(content_id)
        response = requests.get(url, headers=cls.headers)
        response = response.json()
        cast = response.get('cast')
        if not cast: return None
        keys_to_keep = ['known_for_department',
                        'name',
                        'original_name',
                        'popularity']
        response['cast'] = [{key: value for key, value in _dict.items() if key in keys_to_keep} for _dict in cast]
        del response['id']
        return response


