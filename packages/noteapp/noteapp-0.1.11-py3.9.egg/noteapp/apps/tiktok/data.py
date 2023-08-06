class DataGenerate:
    def __init__(self, *args, **kwargs):
        self.index = 0

    def next(self, size=1):
        self.index += size
        if size == 1:
            return {
                "video": "assets/video/video_1.mp4",
                "name": "Vannak Niza🦋",
                "caption": "Morning, everyone!!",
                "song_name": "original sound - Łÿ Pîkâ Ćhûû",
                "profile_pic": "assets/img/image_1.jpg",
                "likes": "1.5M",
                "comments": "18.9K",
                "shares": "80K",
                "album_pic": "assets/img/cover_1.jpg"
            }
        else:
            a = {
                "video": "assets/video/video_1.mp4",
                "name": "Vannak Niza🦋",
                "caption": "Morning, everyone!!",
                "song_name": "original sound - Łÿ Pîkâ Ćhûû",
                "profile_pic": "assets/img/image_1.jpg",
                "likes": "1.5M",
                "comments": "18.9K",
                "shares": "80K",
                "album_pic": "assets/img/cover_1.jpg"
            }
            return [a for i in range(size)]


class DefaultGenerate(DataGenerate):
    def __init__(self, *args, **kwargs):
        super(DefaultGenerate, self).__init__(*args, **kwargs)

        root = './'
        self.data = [
            {
                "video": root + "assets/video/video_1.mp4",
                "name": "Vannak Niza🦋",
                "caption": "Morning, everyone!!",
                "song_name": "original sound - Łÿ Pîkâ Ćhûû",
                "profile_pic": root + "assets/img/image_1.jpg",
                "likes": "1.5M",
                "comments": "18.9K",
                "shares": "80K",
                "album_pic": root + "assets/img/cover_1.jpg"
            },
            {
                "video": root + "assets/video/video_2.mp4",
                "name": "Dara Chamroeun",
                "caption": "Oops 🙊 #fyp #cambodiatiktok",
                "song_name": "original sound - 💛💛Khantana 🌟",
                "profile_pic": root + "assets/img/image_2.jpg",
                "likes": "4.4K",
                "comments": "5.2K",
                "shares": "100",
                "album_pic": root + "assets/img/cover_2.jpg"
            },
            {
                "video": root + "assets/video/video_3.mp4",
                "name": "9999womenfashion",
                "caption": "#블루모드",
                "song_name": "original sound - 🖤Khün MÄk🇰🇭",
                "profile_pic": root + "assets/img/image_3.jpg",
                "likes": "100K",
                "comments": "10K",
                "shares": "8.5K",
                "album_pic": root + "assets/img/cover_3.jpg"
            },
            {
                "video": root + "assets/video/video_4.mp4",
                "name": "Zik Saloo",
                "caption": "Things we do for fun",
                "song_name": "original sound - fearless",
                "profile_pic": root + "assets/img/image_4.jpg",
                "likes": "1.1M",
                "comments": "50K",
                "shares": "10k",
                "album_pic": root + "assets/img/cover_4.jpg"
            },
        ]

        # Icon Unicodes
        # chat bubble: '\U0000E808'
        # share: '\U0000E80E'
        # home: '\U0000E80B'
        # discover: '\U0000E80F'
        # me: '\U0000E80D'
        # message: '\U0000E80C'
        # create: '\U0000E809'
        # heart: '\U0000E80A'

    def next(self, size=1):
        index = self.index % len(self.data)
        if size == 1:
            data = self.data[index]
        else:
            data = self.data[index:index + size]
        self.index += size
        return data
