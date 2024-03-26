from telegrinder.tools import HTMLFormatter, link
from typing import Optional


class Videos:
    class Video:
        def __init__(self, link: Optional[str] = None, message: Optional[str] = None, id: Optional[str] = None):
            self.link = link
            self.message = message
            self.id = id

    video1 = Video("https://www.youtube.com/watch?v=YQFwsG8UGtU", "Как зарегистрироваться в СЭП?", "useful_video_1")
    video2 = Video("https://www.youtube.com/watch?v=nS-PQmCEB_k", "Как оплатить через Сбербанк?", "useful_video_2")


class UsefulVideos:

    @staticmethod
    def get_message(video_id: str) -> str:

        video: Videos().Video()

        if video_id == Videos().video1.id:
            video = Videos().video1
        elif video_id == Videos().video2.id:
            video = Videos().video2

        return f"{HTMLFormatter(link(video.link, video.message))}"



