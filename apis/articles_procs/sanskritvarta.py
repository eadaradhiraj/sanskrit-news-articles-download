from .get_files_base_class import GetFilesBaseClass
from datetime import datetime
from apis.models import NewsArticlePublishTime
from django.utils import timezone
from pytz import timezone as pytz_timezone
localtz = pytz_timezone('Asia/Kolkata')


class Sanskrit_Varta(GetFilesBaseClass):
    url: str = "https://sanskritvarta.in/"

    def get_pdf_content(self) -> list:
        source_name = "sanskritvarta"
        NewsArticlePublishTime_obj = NewsArticlePublishTime.objects.filter(
            source=source_name
        ).first()
        _soup = self.get_soup(self.url)
        all_posts = _soup.find(
            "div", {
                "class": [
                    "aft-frontpage-feature-section-wrapper",
                ]
            }
        ).findAll("div", {"class": "read-details"}) + _soup.find(
            "div", {"class": "content-area"}
        ).findAll("div", {"class": "read-details"})
        art_links = [
            {
                "date": localtz.localize(
                    datetime.strptime(
                        post.find(
                            "span", {"class": "posts-date"}
                        ).text.strip(), "%B %d, %Y"
                    )
                    ),
                "link": post.find(
                    "div", {"class": "read-title"}
                ).find("a").get("href")
            } for post in all_posts
        ]

        return_mail = "https://www.newzviewz.com/sanskrit/home"
        post_date = art_links[0].get("date")

        if not NewsArticlePublishTime_obj:
            return_articles = [
                post.get("link") for post in art_links
            ]
            return_mail += "\n\n\n".join(return_articles)
            NewsArticlePublishTime.objects.create(
                source=source_name,
                timestamp=post_date,
                log="Article(s) Found",
            )
            return [{"content": return_mail, "date": post_date}]
        saved_date = timezone.localtime(NewsArticlePublishTime_obj.timestamp)
        to_save_log = f"{source_name} scraped but no result"
        if post_date > saved_date:
            to_save_log = "Article(s) Found"
            for post in art_links:
                if post.get("date") > saved_date:
                    return_mail += "\n\n\n"+post.get("link")
        NewsArticlePublishTime_obj.timestamp = post_date
        NewsArticlePublishTime_obj.log = to_save_log
        NewsArticlePublishTime_obj.save()
        return [{"content": return_mail, "date": post_date}]
