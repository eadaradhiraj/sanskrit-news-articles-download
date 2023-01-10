from .get_files_base_class import GetFilesBaseClass
from datetime import timedelta


class AIRNSD(GetFilesBaseClass):
    _download_hours = {10: "0655-0700", 23: "1810-1815"}
    domain = "newsonair.gov.in"
    file_name = "nsd-text.aspx"
    protocol = "https://"
    home_page = f"{protocol}{domain}"
    url = f"{protocol}{domain}/{file_name}"
    source = f"{domain}"

    headers = {
        "authority": domain,
        "accept": "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-GB,en;q=0.8",
        "cache-control": "max-age=0",
        "origin": home_page,
        "referer": url,
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "sec-gpc": "1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/106.0.0.0 Safari/537.36",
    }

    def get_eventtarget_elem(self, soup, file_time, curr_time):
        day_in_string = f'{curr_time.day} {curr_time.strftime("%B")}'
        target_text_pattern = (
            f"\n\nSanskrit\n\n{file_time} \n\nDownload\n\n"
            f'{day_in_string}\n\n'
        )
        eventtarget_elem = soup.find(
            lambda tag: tag.name == "tr" and target_text_pattern in tag.text
        )
        return eventtarget_elem, target_text_pattern

    def get_pdf_content(self) -> bytes:
        file_time = self._download_hours.get(self.datetime_now.hour, None)
        if not file_time:
            raise Exception(f"{self.datetime_now.hour} not found")
        soup = self.get_soup(self.url)
        curr_time = self.datetime_now
        eventtarget_elem, target_text_pattern = self.get_eventtarget_elem(
            soup, file_time, curr_time
        )
        if not eventtarget_elem:
            eventtarget_elem, target_text_pattern = self.get_eventtarget_elem(
                soup, self._download_hours[20], curr_time - timedelta(days=1)
            )
            if not eventtarget_elem:
                raise Exception(f"{target_text_pattern} not found")
        EVENTTARGET = eventtarget_elem.find("a")["id"].replace("_", "$")
        data = {
            "__EVENTTARGET": EVENTTARGET,
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": soup.find(
                "input", {"id": "__VIEWSTATE"}
            ).get("value"),
            "__VIEWSTATEGENERATOR": soup.find(
                "input", {"id": "__VIEWSTATEGENERATOR"}
            ).get("value"),
            "__VIEWSTATEENCRYPTED": "",
        }
        return [
            {
                "date": self.datetime_now,
                "content": self.post_request(
                    self.url,
                    headers=self.headers,
                    data=data
                ),
            }
        ]
