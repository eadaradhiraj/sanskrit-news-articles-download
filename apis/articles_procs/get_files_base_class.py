from bs4 import BeautifulSoup as _soup
import requests
from django.utils import timezone
from abc import ABC, abstractmethod


class GetFilesBaseClass(ABC):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    }

    @property
    def datetime_now(self):
        return timezone.localtime(timezone.now())

    def log_requests_failure(self, status_code) -> dict:
        if status_code != 200:
            return self.fail_log(msg=f"{url} retrieval failed with {req.status_code}")

    def get_html(self, url) -> bytes:
        req = requests.get(url, self.HEADERS)
        self.log_requests_failure(status_code=req.status_code)
        return req.content

    def get_soup(self, url) -> _soup:
        return _soup(self.get_html(url), "html.parser")

    def post_request(self, url, headers, data) -> bytes:
        req = requests.post(url=url, headers=headers, data=data)
        self.log_requests_failure(status_code=req.status_code)
        if req.status_code == 200:
            return req.content
        return None

    @abstractmethod
    def get_pdf_content(self):
        return NotImplementedError(
            f"get_pdf_content not implemented for class {self.cls_name}"
        )

    @property
    def cls_name(self) -> str:
        return type(self).__name__

    def logger(self, success, msg) -> dict:
        return {
            "time": self.datetime_now,
            "classname": self.cls_name,
            "success": success,
            "msg": msg,
        }

    def fail_log(self, msg) -> dict:
        return self.logger(success=False, msg=msg)

    def run(self) -> dict:
        try:
            result = self.get_pdf_content()
        except Exception as e:
            return {"result": None, "log": self.fail_log(msg=str(e))}
        appending_result_text = " but no result" if not result else ""
        return {
            "result": result,
            "log": self.logger(
                success=True, msg=f"{self.cls_name} scraped{appending_result_text}"
            ),
        }
