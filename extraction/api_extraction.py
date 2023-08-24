import os
import time
from typing import Union
from typing import Iterator
import json
import requests
from airflow.providers.mongo.hooks.mongo import MongoHook

class TMDBApiData():
    """
    """
    movies_endpoint = "https://api.themoviedb.org/3/trending/movie/week?language=en-US&page={}"
    cast_endpoint = "https://api.themoviedb.org/3/movie/{}/credits?language=en-US"
    headers = {
            "accept": "application/json",
            "Authorization": "Bearer " + os.environ['TMDB_API_TOKEN']
        }
    content_ids = []
    date_of_scraping = None

    @classmethod
    def get_data(cls) -> Iterator:
        """
        """
        page = 1
        while True:
            print(f'Scraping page {page} of TMDB API')
            url = cls.movies_endpoint.format(page)
            response = cls.get_response(url, cls.headers)
            if response.get('success', None) == False or page == 50: break
            results = response.get('results')
            for content in results:
                content_id = content['id']
                if content_id in cls.content_ids: continue
                content['cast'] = cls.get_cast(content_id)
                content['created_at'] = cls.date_of_scraping
                yield content
            page += 1
        print('\n\x1b[1;33;40mAPI Scraping Done!\x1b[0m\n')
    
    @classmethod
    def get_cast(cls, content_id:int) -> Union[None, dict]:
        """
        """
        url = cls.cast_endpoint.format(content_id)
        response = cls.get_response(url, cls.headers)
        cast = response.get('cast')
        if not cast: return None
        keys_to_keep = ['known_for_department',
                        'name',
                        'original_name',
                        'popularity']
        response['cast'] = [{key: value for key, value in _dict.items() if key in keys_to_keep} for _dict in cast]
        del response['id']
        return response
    
    @staticmethod
    def get_response(url:str, headers:dict) -> dict:
        """
        Metodo que hace requests y parsea a JSON.
        Returns: JSON object
        """
        seconds = 10
        tries = 0
        # Errores aleatorios
        while True:
            try:
                response = requests.get(url, headers=headers)
                return response.json()
            except (requests.exceptions.ConnectionError, 
                    requests.exceptions.ChunkedEncodingError,
                    ConnectionError) as e:
                assert tries < 10, f'10 tries reached with url -> {url}, exception -> {e}'
                time.sleep(seconds)
                seconds += 5
                tries += 1
                continue


