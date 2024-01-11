from abc import ABC, abstractmethod
from requests import request
import time
from random import choices
from hashlib import sha512
from string import ascii_letters
from pprint import pprint  # TODO: remove when won't be used

from .models import Contest, Submission, Order


class BasicApi(ABC):
    def __init__(self, contest: Contest):
        self.contest = contest

    @abstractmethod
    def query_api(self, api_method: str, http_method: str, **params):
        pass

    @abstractmethod
    def fetch_and_cache_all_submits(self):
        pass

    def make_new_orders(self):
        submissions = Submission.objects.filter(
            contest=self.contest,
            verdict=Submission.Verdict.OK
        ).order_by('time_from_start')
        for submission in submissions:
            if Order.objects.filter(submission__author=submission.author,
                                    submission__problem_index=submission.problem_index).count() > 0:
                continue
            Order.create_order_for_submission(submission)

    def process_all_submits(self):
        self.fetch_and_cache_all_submits()
        self.make_new_orders()


class YandexContestAPI(BasicApi):
    def __init__(self, contest: Contest):
        super().__init__(contest)
        self.api_url = "https://api.contest.yandex.net/api/public/v2/"

    def query_api(self, api_method: str, http_method: str, **params):
        response = request(
            method=http_method,
            url=self.api_url + api_method,
            headers={'Authorization': f'OAuth {self.contest.api_key}'},
            params=params
        )
        if response.status_code != 200:  # FIXME: tune for YandexContest behavior
            time.sleep(2)  # FIXME: more adequate error handling!!!
            return self.query_api(api_method, http_method, **params)
        return response.json()

    def fetch_and_cache_all_submits(self):
        yc_submissions = self.query_api(
            f'contests/{self.contest.external_id}/submissions',
            http_method='GET',
            page=1,
            pageSize=100000,  # TODO: check that this pageSize works fine
        )
        pprint(yc_submissions)

        for yc_sub in yc_submissions['submissions']:
            if 'timeFromStart' not in yc_sub:
                continue
            # FIXME: develop normal validation for non-real participants (managers, virtuals, etc)
            # TODO: check when timeFromStart would be missing

            try:
                db_sub = Submission.objects.get(contest=self.contest, external_id=yc_sub['id'])
            except Submission.DoesNotExist:
                db_sub = Submission()

            db_sub.external_id = yc_sub['id']
            db_sub.contest = self.contest
            db_sub.problem_index = yc_sub['problemAlias']
            db_sub.author = yc_sub['author']
            db_sub.time_from_start = yc_sub['timeFromStart'] // 1000
            if yc_sub['verdict'] == 'TESTING':  # TODO: check this exact keyword!!!
                db_sub.verdict = Submission.Verdict.TESTING
            elif yc_sub['verdict'] == 'OK':
                db_sub.verdict = Submission.Verdict.OK
            else:
                db_sub.verdict = Submission.Verdict.OTHER
            db_sub.save()


class CodeforcesAPI(BasicApi):
    def __init__(self, contest: Contest):
        super().__init__(contest)
        self.api_url = "https://codeforces.com/api/"

    def query_api(self, api_method: str, http_method: str, **params) -> dict:
        params['lang'] = 'ru'
        params['apiKey'] = self.contest.api_key
        params['time'] = int(time.time())
        random_signature_prefix = ''.join(choices(ascii_letters, k=6))
        query_str = f'{random_signature_prefix}/{api_method}?'
        query_str += '&'.join([f'{param}={value}' for param, value in
                               sorted(list(map(lambda pair: (str(pair[0]), str(pair[1])), params.items())))])
        query_str += f'#{self.contest.api_secret}'
        params['apiSig'] = random_signature_prefix + sha512(query_str.encode()).hexdigest()

        print(query_str)

        response = request(
            method=http_method,
            url=self.api_url + api_method,
            params=params,
        )
        if response.status_code != 200 or response.json()['status'] != 'OK':
            time.sleep(2)  # FIXME: more adequate error handling!!!
            return self.query_api(api_method, http_method, **params)
        pprint(response.json())
        return response.json()['result']

    def fetch_and_cache_all_submits(self):
        cf_submissions = self.query_api(
            'contest.status',
            http_method='GET',
            contestId=self.contest.external_id,
            asManager=True,
        )
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
            db_sub.problem_index = cf_sub['problem']['index']
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
