from .get_files_base_class import GetFilesBaseClass
from datetime import datetime
from apis.models import NewsArticlePublishTime


class Sanskrit_Varta(GetFilesBaseClass):
    url: str = "https://sanskritvarta.in/"

    def get_post_info(self, post) -> dict:
        post_soup = self.get_soup(post.find('a').get("href"))
        date_of_post = post.find(
            'span', {'class': 'posts-date'}
        ).text.strip()
        post_content = '\n'.join(
            [
                p.text.strip() for p in post_soup.findAll(
                    "p", attrs={
                        "style": "text-align: justify;"
                    }
                )
            ]
        )
        postno = [
            cls.split("-")[1] for cls in post_soup.find(
                "body"
            ).get("class") if cls.startswith("postid")
        ][0]
        return {
            "date": datetime.strptime(date_of_post, "%B %d, %Y"),
            "content": post_content,
            "postno": int(postno)
        }

    def get_all_articles(self) -> list:
        _soup = self.get_soup(self.url)
        top_trending_posts = _soup.find(
            'div', {'id': 'aft-main-banner-latest-trending-popular-recent'}
        ).findAll("li")
        return [
            self.get_post_info(post) for post in top_trending_posts
        ]

    def get_pdf_content(self) -> list:
        source_name = "sanskritvarta"
        NewsArticlePublishTime_obj = NewsArticlePublishTime.objects.filter(
            source=source_name
        ).first()
        articles = self.get_all_articles()
        return_articles = []
        postno = articles[0].get("postno")
        if not NewsArticlePublishTime_obj:
            NewsArticlePublishTime.objects.create(
                source=source_name,
                timestamp=articles[0].get("date"),
                log="Article(s) Found",
                postno=postno
            )
            return articles
        saved_postno = NewsArticlePublishTime_obj.postno
        to_save_log = "Articles Found"
        if postno > saved_postno:
            return_articles.append(articles[0])
            return_articles.extend(
                [
                    article for article in articles
                    if article.get("postno") > saved_postno
                ]
            )
            to_save_log = f"{source_name} scraped but no result"
        NewsArticlePublishTime_obj.timestamp = articles[0].get("date")
        NewsArticlePublishTime_obj.log = to_save_log
        NewsArticlePublishTime.postno = postno
        NewsArticlePublishTime_obj.save()
        return return_articles
