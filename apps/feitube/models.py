# -*- coding:utf-8 -*-
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.conf import settings
from django.contrib.auth.models import User
import uuid
import os
from time import strftime

#											PROFILE
##########################################################################################
def get_file_path_profiles(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('images/profiles', filename)

def get_file_path_covers(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('images/covers', filename)
        
class Profile(models.Model):
    '''Perfiles de los usuarios de FEITUBE. Cuenta con atributos básicos: nombre,
    apellidos, username, password que obtiene de una asociación uno a uno con
    con el modelo USER de django, además de los descritos abajo.'''
    user = models.OneToOneField(User)
    facebook = models.URLField('Facebook', max_length=255, blank=True, null=True, default='http://localhost:8000')
    twitter = models.URLField('Twitter', max_length=255, blank=True, null=True, default='http://localhost:8000')
    instagram = models.URLField('Instagram', max_length=255, blank=True, null=True, default='http://localhost:8000')
    google = models.URLField('Google +', max_length=255, blank=True, null=True, default='http://localhost:8000')
    profile_picture = models.FileField(upload_to=get_file_path_profiles, blank=True, null=True)
    cover_picture = models.FileField(upload_to=get_file_path_covers, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def save(self):
        self.slug = slugify(str(self.user.get_username()))
        super(Profile, self).save()

    def __str__(self):
        return self.user.get_username()



#											VIDEO
##########################################################################################
def get_file_path_videos(instance, filename):
	extension = filename.split('.')[-1]
	folder = instance.slug
	filename = folder + '.' + extension
	return os.path.join('videos/' + folder, filename)

class Video(models.Model):
    '''Representación de los videos mostrados en FEITUBE. Pueden ser comentados,
    calificados, agregados a favoritos o PLAYLISTs.'''
    title = models.CharField('Título', max_length=255)
    tags = models.CharField('Tags', max_length=255)
    description = models.TextField ('Descripción')
    path = models.FileField(upload_to=get_file_path_videos)
    generic_path = models.CharField('Ruta genérica', max_length=255)
    views = models.IntegerField ('Visitas', blank=True, null=True)
    uploaded = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(Profile, verbose_name='Usuario', related_name='videos', blank=True, null=True)
    favs_count = models.IntegerField ('Cantidad de favoritos', blank=True, null=True)
    favs = models.ManyToManyField(Profile, verbose_name='Favoritos', related_name='videos_fav', blank=True)
    rates_count = models.IntegerField('Total de calificaciones', blank=True, null=True)
    rates_sum = models.IntegerField('Suma total de calificaciones', blank=True, null=True)
    rates = models.ManyToManyField(Profile, verbose_name='Calificaciones', through="Rate", 
    						through_fields=('video', 'profile'), related_name='videos_rate')
    comments = models.ManyToManyField(Profile, verbose_name='Comentarios', through="Comment", 
    						through_fields=('video', 'profile'), related_name='videos_comment')
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'

    def save(self):
        self.slug = slugify(str(self.title))
        super(Video, self).save()

    def __str__(self):
        return self.title


#											RATE
##########################################################################################
class Rate(models.Model):
	'''Calificación otorgada por los usuarios a los videos. Un video es calificado por
	varios usuarios, y un usuario puede calificar varios videos. Escala 1-5'''
	video = models.ForeignKey(Video, related_name='video_rates')
	profile = models.ForeignKey(Profile, related_name='profile_rates')
	score = models.IntegerField('Puntuación')

	class Meta:
		verbose_name = 'Calificación'
		verbose_name_plural = 'Calificaciones'

	def __str__(self):
		return str(self.score)


#											COMMENT
##########################################################################################
class Comment(models.Model):
    '''Comentarios de los usuario sobre los videos. Un video puede ser comentado por
    varios usuarios, y un usuario puede comentar varios videos.'''
    video = models.ForeignKey(Video, related_name='video_comments')
    profile = models.ForeignKey(Profile, related_name='profile_comments')
    comment = models.TextField('Comentario')
    published = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'

    def __str__(self):
        return self.comment



#											PLAYLIST
##########################################################################################
class Playlist(models.Model):
    '''Listas de reproducción de VIDEOs guardadas por el usuario.'''
    title = models.CharField('Título', max_length=255)
    amount = models.IntegerField ('Cantidad')
    profile = models.ForeignKey(Profile, verbose_name='Usuario', related_name='playlist')
    videos = models.ManyToManyField(Video)

    class Meta:
        verbose_name = 'Playlist'
        verbose_name_plural = 'Playlists'

    def save(self):
        self.slug = slugify(str(self.title))
        super(Playlist, self).save()

    def __str__(self):
        return self.title