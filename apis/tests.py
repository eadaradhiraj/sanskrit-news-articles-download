import pytest
from apis.models import NewsArticlePublishTime
from django.utils import timezone
from freezegun import freeze_time
import datetime

fake_timenow = timezone.localtime(timezone.now())
morning_time = 10
eve_time = 23
if fake_timenow.hour < morning_time:
    fake_timenow = fake_timenow.replace(hour=eve_time, day=fake_timenow.day - 1)
elif 11 <= fake_timenow.hour < eve_time:
    fake_timenow = fake_timenow.replace(hour=morning_time)
elif fake_timenow.hour > eve_time:
    fake_timenow = fake_timenow.replace(hour=eve_time)


def test_nsd_articles(client, mailoutbox):
    response = client.get("/apis/save-nsd-articles")
    assert response.status_code == 200
    assert len(mailoutbox) == 1
    if "not found" not in response.data.get("msg"):
        assert bool(mailoutbox[0].attachments)


@pytest.mark.django_db(True)
class TestApiModel:
    @freeze_time(fake_timenow)
    def test_nsd_articles_1(self, client, mailoutbox):
        test_nsd_articles(client, mailoutbox)

    @freeze_time(fake_timenow - datetime.timedelta(hours=12))
    def test_nsd_articles_2(self, client, mailoutbox):
        test_nsd_articles(client, mailoutbox)

    @freeze_time(fake_timenow.replace(hour=13))
    def test_nsd_articles_3(self, client, mailoutbox):
        response = client.get("/apis/save-nsd-articles")
        assert len(mailoutbox) == 1
        assert "not found" in response.data.get("msg")

    def test_nsd_articles_sanskritvarta(self, client, mailoutbox):
        response = client.get("/apis/save-sanskritvarta-articles")
        assert len(mailoutbox) == 1
        assert "classname" in response.data.keys()

    def test_other_articles(self, client, mailoutbox):
        sources = {
            "SampratiVartah": "save-samprativartah-articles",
            "SampratiVartahLiterature": "save-samprativartah-lit-articles",
        }
        for source_name, source_endp in sources.items():
            source_url = f"/apis/{source_endp}"
            response = client.get(source_url)
            news_time = NewsArticlePublishTime.objects.filter(
                source=source_name
            ).first()
            assert len(mailoutbox) > 0
            assert hasattr(news_time, "timestamp")
            assert response.status_code == 200
            resp_dates = response.data.get("dates")
            for i in range(0, 3):
                news_time.timestamp = resp_dates[i]
                news_time.save()
                mailoutbox.clear()
                response = client.get(source_url)
                if len(mailoutbox) == 0:
                    assert "no result" in response.data.get('msg')
                else:
                    assert len(mailoutbox) > 0
