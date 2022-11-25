import pytest


@pytest.mark.django_db(True)
class TestApiModel():
    def test_nsd_articles(self, client, mailoutbox):
        response = client.get(
            '/apis/save-nsd-articles'
        )
        assert len(mailoutbox) == 1
        assert response.status_code == 200

    def test_samprati_articles(self, client, mailoutbox):
        response = client.get(
            '/apis/save-samprativartah-articles'
        )
        assert len(mailoutbox) > 1
        assert response.status_code == 200

    def test_samprati_lit_articles(self, client, mailoutbox):
        response = client.get(
            '/apis/save-samprativartah-lit-articles'
        )
        assert len(mailoutbox) > 1
        assert response.status_code == 200
