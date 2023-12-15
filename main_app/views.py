from django.shortcuts import render

from .models import Contest
from .api import BasicApi, YandexContestAPI, CodeforcesAPI

# Create your views here.


def test(request, contest_id: int):
    contest = Contest.objects.get(external_id=contest_id, test_system=Contest.TestSystem.CODEFORCES)
    api = CodeforcesAPI(contest)
    api.fetch_and_cache_all_submits()
