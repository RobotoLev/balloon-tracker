from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Contest, Order
from .api import BasicApi, YandexContestAPI, CodeforcesAPI

# Create your views here.


def test_codeforces(request, contest_id: int):
    contest = Contest.objects.get(external_id=contest_id, test_system=Contest.TestSystem.CODEFORCES)
    api = CodeforcesAPI(contest)
    api.process_all_submits()


def test_yandex_contest(request, contest_id: int):
    contest = Contest.objects.get(external_id=contest_id, test_system=Contest.TestSystem.YANDEX_CONTEST)
    api = YandexContestAPI(contest)
    api.process_all_submits()


def index(request):
    return render(request, 'index.html')


@login_required
def volunteer_profile(request):
    volunteer = request.user

    return render(request, 'profile.html', context={
        "orders": Order.objects.filter(volunteer=volunteer).all()
    })
