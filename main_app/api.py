from abc import ABC, abstractmethod
from requests import get
import time
from random import randint
from hashlib import sha512
from pprint import pprint  # TODO: remove when won't be used

from .models import Contest, Submission


class BasicApi(ABC):
    def __init__(self, contest: Contest):
        self.contest = contest

    @abstractmethod
    def query_api(self, method: str, **params):
        pass

    # @abstractmethod
    def fetch_and_cache_all_submits(self):
        pass


class YandexContestAPI(BasicApi):
    def __init__(self, contest: Contest):
        super().__init__(contest)
        self.api_url = ""  # TODO

    def query_api(self, method: str, **params):
        pass

    def fetch_and_cache_all_submits(self):
        pass


class CodeforcesAPI(BasicApi):
    def __init__(self, contest: Contest):
        super().__init__(contest)
        self.api_url = "https://codeforces.com/api/"

    def query_api(self, method: str, **params) -> dict:

        params['lang'] = 'ru'
        params['apiKey'] = self.contest.api_key
        params['time'] = int(time.time())
        random_signature_prefix = ''.join([str(randint(0, 9)) for _ in range(6)])
        query_str = f'{random_signature_prefix}/{method}?'
        query_str += '&'.join([f'{param}={value}' for param, value in sorted(list(params.items()))])
        query_str += f'#{self.contest.api_secret}'
        params['apiSig'] = random_signature_prefix + sha512(query_str.encode()).hexdigest()

        print(query_str)

        response = get(
            url=self.api_url + method,
            params=params
        )
        if response.status_code != 200 or response.json()['status'] != 'OK':
            time.sleep(2) # TODO: more adequate error handling!!!
            self.query_api(method, **params)
        return response.json()['result']

    def fetch_and_cache_all_submits(self):
        pprint(self.query_api('contest.status', contestId=self.contest.external_id, asManager=True))  # TODO: add saving
