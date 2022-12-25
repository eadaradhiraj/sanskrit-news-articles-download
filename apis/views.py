from rest_framework.decorators import api_view
from rest_framework.response import Response
from .articles_procs import (
    airnsd,
    samprativartah,
    sanskritvarta
)
from django.conf import settings
from django.core.mail import EmailMessage
from common.logging import logger


article_class_dict = {
    "SampratiVartahLiterature": samprativartah.SampratiVartahLiterature(),
    "SampratiVartah": samprativartah.SampratiVartah(),
    "sanskritvarta": sanskritvarta.Sanskrit_Varta()
}


def save_samprati_articles_common(source_name):
    samprativartah_obj = article_class_dict.get(source_name)
    if not samprativartah_obj:
        return Response()
    samprativartah_article = samprativartah_obj.run()
    logger.info(samprativartah_article.get("log"))
    mail = EmailMessage(
        from_email=settings.EMAIL_HOST_USER,
        to=["eadaradhiraj@gmail.com"],
    )
    results = samprativartah_article.get("result")
    if results:
        for result in results:
            mail.body = result.get("content")
            mail.subject = f"{source_name} @{result.get('date')}"
            mail.send()
    return Response(samprativartah_article.get("log"))


@api_view(["GET"])
def save_samprati_lit_articles(_):
    return save_samprati_articles_common("SampratiVartahLiterature")


@api_view(["GET"])
def save_samprati_news_articles(_):
    return save_samprati_articles_common("SampratiVartah")


@api_view(["GET"])
def save_sanskritvarta_articles(_):
    return save_samprati_articles_common("sanskritvarta")


@api_view(["GET"])
def save_nsd_articles(_):
    airnsd_obj = airnsd.AIRNSD()
    _nsd_article = airnsd_obj.run()
    logger.info(_nsd_article.get("log"))
    mail = EmailMessage(
        subject=f"NSD @{airnsd_obj.datetime_now}",
        from_email=settings.EMAIL_HOST_USER,
        to=["eadaradhiraj@gmail.com"],
    )
    if _nsd_article.get("result"):
        mail.attach(
            "news.pdf",
            _nsd_article["result"][0].get("content"),
            "application/pdf"
        )
    else:
        mail.body = _nsd_article.get("log").get("msg")
    mail.send()
    return Response(_nsd_article.get("log"))
