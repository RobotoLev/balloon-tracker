from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.


class User(AbstractUser):
    pass


# TODO: pretty tables in admin for Contest and Submission


class Contest(models.Model):
    class TestSystem(models.IntegerChoices):
        YANDEX_CONTEST = 1, _("Яндекс.Контест")
        CODEFORCES = 2, _("Codeforces")

    external_id = models.IntegerField(
        verbose_name="Внешний ID контеста",
    )
    test_system = models.IntegerField(
        choices=TestSystem.choices,
        verbose_name="Тестирующая система",
    )
    api_key = models.CharField(
        max_length=250,
        verbose_name="API-ключ для доступа к соревнованию",
    )
    api_secret = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="API-секрет, если требуется",
    )

    @property
    def test_system_label(self):
        return self.TestSystem(self.test_system).label

    def __str__(self):
        return f"{self.test_system_label} {self.external_id}"

    class Meta:
        verbose_name = "контест"
        verbose_name_plural = "контесты"


class Submission(models.Model):
    class Verdict(models.IntegerChoices):
        TESTING = 1, _("Тестируется")
        OK = 2, _("Полное решение")
        OTHER = 3, _("Иной вердикт")

    external_id = models.BigIntegerField(
        verbose_name="Внешний ID посылки",
    )
    contest = models.ForeignKey(
        'Contest',
        on_delete=models.PROTECT,
        related_name='submissions',
        related_query_name='submission',
        verbose_name='Контест',
    )
    author = models.CharField(
        max_length=100,
        verbose_name="Никнейм участника",
    )
    time_from_start = models.IntegerField(
        verbose_name="Время от начала контеста до попытки (в секундах)"
    )
    verdict = models.IntegerField(
        choices=Verdict.choices,
        verbose_name="Вердикт посылки",
    )

    def __str__(self):
        return f"{self.contest.test_system_label} {self.contest.external_id} | {self.external_id}"

    class Meta:
        verbose_name = "посылка"
        verbose_name_plural = "посылки"
