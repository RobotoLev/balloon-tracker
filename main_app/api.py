from abc import ABC, abstractmethod
from requests import get
import time
from random import choices
from hashlib import sha512
from string import ascii_letters
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
        random_signature_prefix = ''.join(choices(ascii_letters, k=6))
        query_str = f'{random_signature_prefix}/{method}?'
        query_str += '&'.join([f'{param}={value}' for param, value in
                               sorted(list(map(lambda pair: (str(pair[0]), str(pair[1])), params.items())))])
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
        cf_submissions = self.query_api('contest.status', contestId=self.contest.external_id, asManager=True)
        # pprint(cf_submissions)

        for cf_sub in cf_submissions:
            if cf_sub['author']['participantType'] != 'CONTESTANT':
                continue
            try:
                db_sub = Submission.objects.get(contest=self.contest, external_id=cf_sub['id'])
            except Submission.DoesNotExist:
                db_sub = Submission()

            db_sub.external_id = cf_sub['id']
            db_sub.contest = self.contest
            db_sub.author = cf_sub['author'].get('teamName', cf_sub['author']['members'][0]['handle'])
            db_sub.time_from_start = cf_sub['relativeTimeSeconds']
            if cf_sub['verdict'] == "TESTING":
                db_sub.verdict = Submission.Verdict.TESTING
            elif cf_sub['verdict'] == "OK":
                db_sub.verdict = Submission.Verdict.OK
            else:
                db_sub.verdict = Submission.Verdict.OTHER
            db_sub.save()

            print(db_sub)
