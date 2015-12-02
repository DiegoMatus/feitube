from django.contrib import admin
from apps.feitube.models import Profile, Video, Playlist, Rate, Comment
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Register your models here.
# Define an inline admin descriptor for Profile model
# which acts a bit like a singleton
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profiles'

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (ProfileInline, )

class VideoAdmin (admin.ModelAdmin):
	list_display = ( 'title', 'tags', 'description', 'uploaded')
	list_filter = [ 'profile' ]

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(Video, VideoAdmin)
admin.site.register(Playlist)
admin.site.register(Rate)
admin.site.register(Comment)