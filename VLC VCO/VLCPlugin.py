import vlc
import time

instance = vlc.get_default_instance()
player = instance.media_player_new()
media = player.media_new("vid.mp4")
#player.set_media(instance.media_new("https://neptun.cizgifilmlerizle.com/getvid?evid=qUP-ALy6_u9jY-V5H07BJilDMoaKn-Y_Z2BFIryOxk0bfdACm0sf1_xwr6bfYrMht_SF6t5CO-DBH5IpqkMMcpzpzU1eTFHlcNJRSS26Yn9HWxsX1XjNXwT7go-esyoGzMhjGItvlROL1ORPMeWNswhMiJKgm1Tt97Rv_-uL1QUHmcCONadXmXaMmvMj9Y8wR9DUu8Z0y0j9mG7bgctH-1JZn5_kLWXAdmEVxE8Z2AQMoBuM4lq-1iGfU9Vsu_GqXYVVNXeJct6uACp1fugqtOKcN-VBMGwRP6q4ZkyEAI_i5_08TzN08pPsoqXIHNIL_LvwXhGIuI2EGotPz2iUtr_nu7Q0yrD_Hv4ydoENuCQ"))
player.play()
time.wait(10)
player.stop()
