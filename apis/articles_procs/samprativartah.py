from .get_files_base_class import GetFilesBaseClass
from apis.models import NewsArticlePublishTime
from django.utils.dateparse import parse_datetime
from datetime import datetime


def get_proper_date(result_div, source_name):
    if source_name == "SampratiVartah":
        dt = result_div.find("abbr", {"class": "published"}).get("title")
        date_obj = parse_datetime(dt)
    elif source_name == "SampratiVartahLiterature":
        dt = result_div.find("h2", {"class": "date-header"}).text.strip()
        date_obj = datetime.strptime(f"{dt} +0530", "%A, %d %B %Y %z")
    return date_obj


def parse_rest_articles(results_div, source_name, NewsArticlePublishTime_obj):
    articles = []
    for result_div in results_div:
        res_date_obj = get_proper_date(result_div, source_name)
        if res_date_obj > NewsArticlePublishTime_obj.timestamp:
            articles.append(
                {
                    "date": res_date_obj,
                    "content": result_div.find(
                        "div", {"class": "entry-content"}
                    ).text.strip(),
                }
            )
    return articles


def get_pdf_content_common(_soup, source_name):
    post_class = {
        "SampratiVartah": "post-outer",
        "SampratiVartahLiterature": "date-outer",
    }
    results_div = _soup.find_all("div", {"class": post_class[source_name]})
    if results_div:
        NewsArticlePublishTime_obj = NewsArticlePublishTime.objects.filter(
            source=source_name
        ).first()
        date_obj = get_proper_date(results_div[0], source_name)

        if NewsArticlePublishTime_obj:
            if date_obj > NewsArticlePublishTime_obj.timestamp:
                NewsArticlePublishTime_obj.timestamp = date_obj
                return_articles = parse_rest_articles(
                    results_div, source_name, NewsArticlePublishTime_obj
                )
                NewsArticlePublishTime_obj.save()
                return return_articles
            else:
                NewsArticlePublishTime_obj.log = "No New Results Yet"
                NewsArticlePublishTime_obj.save()
        else:
            NewsArticlePublishTime.objects.create(
                source=source_name, timestamp=date_obj, log="Article(s) Found"
            )
            return [
                {
                    "date": get_proper_date(result_div, source_name),
                    "content": result_div.find(
                        "div", {"class": "entry-content"}
                    ).text.strip(),
                }
                for result_div in results_div
            ]
    return []


class SampratiVartahLiterature(GetFilesBaseClass):
    url = "https://samprativartah.blogspot.com/"

    def get_pdf_content(self) -> str:
        return get_pdf_content_common(
            self.get_soup(self.url),
            "SampratiVartahLiterature",
        )


class SampratiVartah(GetFilesBaseClass):
    url = "http://newssanskrit.blogspot.com"

    def get_pdf_content(self) -> str:
        return get_pdf_content_common(
            self.get_soup(self.url),
            "SampratiVartah",
        )
