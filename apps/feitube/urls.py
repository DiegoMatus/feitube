from django.conf.urls import include, url, patterns
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('apps.feitube.views',
    url(r'^$', 					'index', 				name='index'),
    url(r'^login', 				'login_view', 			name='login'),
    url(r'^logout', 			'logout_view', 			name='logout'),
    url(r'^signup', 			'signup_view', 			name='signup'),
    url(r'^search',             'search_view',          name='search'),
    url(r'^rate',               'rate_view', 			name='rate'),
    url(r'^upload/video', 		'upload_video_view', 	name='upload_video'), #coloque before AJAX
    url(r'^comment', 			'public_comment_view', 	name='public_comment'),
    url(r'^watch/(?P<video_slug>[\w|\W]+)/$',		'video_view',		name='video'),
    url(r'^channel/(?P<username_slug>[\w|\W]+)/(?P<tab>[\w|\W]+)/$',	'channel_view',		name='channel'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 	#Servir estáticos en desarrollo