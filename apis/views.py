from rest_framework.decorators import api_view
from rest_framework.response import Response
from .articles_procs import airnsd
from django.conf import settings
from django.core.mail import EmailMessage
from common.logging import logger


@api_view(["GET"])
def save_nsd_articles(request):
    airnsd_obj = airnsd.AIRNSD()
    _nsd_article = airnsd_obj.run()
    logger.info(_nsd_article.get("log"))
    mail = EmailMessage(
        subject=f"NSD @{airnsd_obj.datetime_now}",
        from_email=settings.EMAIL_HOST_USER,
        to=["eadaradhiraj@gmail.com"],
    )
    if _nsd_article.get("result"):
        mail.attach("news.pdf", _nsd_article.get("result"), "application/pdf")
    else:
        mail.body = _nsd_article.get("log").get("msg")
    mail.send()
    return Response(_nsd_article.get("log"))
