from telegrinder.tools import HTMLFormatter, link, escape, bold
from typing import Optional


class Videos:
    class Video:
        def __init__(self,
                     link_rutube: Optional[str] = None,
                     link_youtube: Optional[str] = None,
                     link_dzen: Optional[str] = None,
                     link_vk: Optional[str] = None,
                     message: Optional[str] = None,
                     id: Optional[str] = None):

            self.link_rutube = link_rutube
            self.link_youtube = link_youtube
            self.link_dzen = link_dzen
            self.link_vk = link_vk
            self.message = message
            self.id = id

    useful_video1 = Video("https://rutube.ru/video/9336b2c5a62a9f6470006c49a2df874b/?r=wd",
                   "https://youtu.be/r6Mm4YBgIwU",
                   "https://dzen.ru/video/watch/66ac75656d1ffe195167038f?share_to=link",
                   "https://vk.com/video-211743331_456239154",
                   "всё о процессе таможенного оформления | \"растаможки\" автомобиля",
                   "useful_video_1")

    useful_video2 = Video("https://rutube.ru/video/ea7f3074a6d6406913f2f188651d0089/",
                   "https://youtu.be/8l1FnLdrUp8",
                   "https://dzen.ru/video/watch/66dea0ba6f233e4b192bb329?share_to=link",
                   "https://vk.com/video-211743331_456239172",
                   "про полный перечень документов и сведений необходимых для таможенного оформления импортных грузов",
                   "useful_video_2")

    useful_video3 = Video("https://rutube.ru/video/c038af756f1c593073d710a28c4f6251/",
                   "https://youtu.be/nS-PQmCEB_k?si=DQ8Efw10TZBOUgRS",
                   "https://dzen.ru/video/watch/66ac7d38011b5c31b22e9c7a",
                   "https://vk.com/video-211743331_456239038",
                   "как оплатить таможенные платежи через приложение СберБанка Онлайн.",
                   "useful_video_3")

    useful_video4 = Video("https://rutube.ru/video/3700588700c08eab719b51b4244654fb/",
                   "https://www.youtube.com/watch?v=YQFwsG8UGtU",
                   "https://dzen.ru/video/watch/66ac7f6e8076ef641486996a",
                   "https://vk.com/video-211743331_456239065",
                   "как зарегистрироваться в системе электронных паспортов (СЭП) для получения электронного ЭПТС?",
                   "useful_video_4")

    useful_video5 = Video("https://rutube.ru/video/27fdbda22e2e3c01363beffb4df05ff3/",
                   "https://youtu.be/Mi4ToqZ20RE",
                   "https://dzen.ru/video/watch/66b2f7e2ad8f77488e5e0c28",
                   "https://vk.com/video-211743331_456239152",
                   "всё про утилизационный сбор и ответили на ваши вопросы",
                   "useful_video_5")

    useful_video6 = Video("https://rutube.ru/video/121f418798a74edc2de41406d44f4285/",
                   "https://www.youtube.com/watch?v=0pgPW5GDbCM",
                   "https://dzen.ru/video/watch/66c5788224005a7b57a0f4c9?rid=3552684348.1126.1724393784693.27878",
                   "https://vk.com/video/@vlbroker/all?z=video-211743331_456239161%2Fclub211743331",
                   "всё про Перестой🔹Реальные причины увеличения сроков таможенного оформления | А также как узнать тарифы СВХ во Владивостоке.",
                   "useful_video_6")

    useful_video7 = Video("https://rutube.ru/video/d02a4b6c73ace763ebcbad059e5af57d/?r=wd",
                   "https://youtu.be/5Hoqn09vsgA",
                   "https://dzen.ru/video/watch/6705e8ebbadccb61694f78ad?share_to=link",
                   "https://vk.com/video-211743331_456239123",
                   "о том, что такое параллельный импорт?🔹 Законная схема в России 2024! Ввоз санкционных автомобилей и товаров",
                   "useful_video_7")

    useful_video8 = Video("https://rutube.ru/video/1efce3f2aca406bff07ebeedc1126963/",
                   "https://youtu.be/ILALgM-T16Q?si=wbdQaAsD_xbBRecj",
                   "https://dzen.ru/video/watch/66ed0f73cc4c5a16f7420947?share_to=link",
                   "https://vk.com/video-211743331_456239177?access_key=8b74781a131b129c82",
                   "о импорте товаров в Россию: выбор, сертификация, пошлина, код ТН ВЭД🔹Советы таможенного эксперта!",
                   "useful_video_8")

    VIDEOS = [
        useful_video1,
        useful_video2,
        useful_video3,
        useful_video4,
        useful_video5,
        useful_video6,
        useful_video7,
        useful_video8
    ]


class UsefulVideos:

    @staticmethod
    def get_message(video_id: str) -> str:

        video: Videos().Video() = None

        for video in Videos().VIDEOS:
            if video_id == video.id:
                break

        return f"""
{HTMLFormatter(escape("В нашем видео рассказали "))}{HTMLFormatter(bold(video.message))}

{HTMLFormatter(bold(escape("Переходите к просмотру на удобных для вас платформах:")))}
{HTMLFormatter(link(video.link_rutube, "🔹RUTUBE"))}
{HTMLFormatter(link(video.link_vk, "🔹VK Видео"))}
{HTMLFormatter(link(video.link_dzen, "🔹Дзен"))}
{HTMLFormatter(link(video.link_youtube, "🔹YouTube"))}

{HTMLFormatter(bold(escape("Благодарим, что остаётесь с нами!")))}
"""



