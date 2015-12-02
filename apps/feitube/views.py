from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.feitube.models import Profile, Video, Comment, Rate
from apps.feitube.tasks import video_encode
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.hashers import make_password

########################################VIEWS######################################

#										INDEX VIEW
##########################################################################################
def index(request):
	'''Home. Carga la lista de videos subidos'''
	videos = Video.objects.all()
	context = { 'videos': videos }
	return render(request, 'index.html', context)


#										LOGIN VIEW
##########################################################################################
@csrf_exempt
def login_view(request):
	'''Home. Carga la lista de videos subidos'''
	if request.method == "POST":	
	    username = request.POST['username']
	    password = request.POST['password']
	    user = authenticate(username=username, password=password)
	    if user is not None:
	        if user.is_active:
	            login(request, user)
	            return redirect(request.META.get('HTTP_REFERER'))
	    else:
	    	return render(request, '500.html', {'error': "Usuario y/o contraseña incorrecta"})
	return render(request, '500.html')
		


#										LOGOUT VIEW
##########################################################################################
@login_required(login_url='/')
def logout_view(request):
	logout(request)
	return redirect('index')

	
#										SIGNUP VIEW
##########################################################################################
@csrf_exempt
def signup_view(request):
	if request.method == "POST":
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
		email = request.POST['email']
		username = request.POST['username']
		password = request.POST['password']
		confirm_password = request.POST['password2']
		profile_picture = request.FILES.get('profile_picture')

		try:
			if password == confirm_password:
				password = make_password(password)
				confirm_password = make_password(confirm_password)

				user = User(username=username, first_name=first_name, last_name=last_name, email=email,
					password=password)
				user.save()

				profile = Profile(user=user, profile_picture=profile_picture)
				profile.save()

				return redirect('index')
			else:
				return render(request, '500.html', {'error': "Las contraseñas no coinciden"})
		except:
			return render(request, '500.html', {'error': "El username ya existe"})


#										SEARCH VIEW
##########################################################################################
def search_view(request):
	if request.method == "POST":
		query = request.POST['search']
		video_results = Video.objects.filter(Q(title__icontains=query) | Q(tags__icontains=query) | Q(description__icontains=query)).order_by('uploaded')
		context = { 'videos': video_results}
		return render(request, 'search.html', context)
	else:
		return redirect(request.META.get('HTTP_REFERER'))


	
#										UPLOAD VIDEO VIEW
##########################################################################################
@csrf_exempt
def upload_video_view(request):
	if request.method == 'POST':
		try:
			user = request.user
			video_profile = Profile.objects.get(user=user)

			video_title = request.POST.get("video_title")
			video_tags = request.POST.get("video_tags")
			video_description = request.POST.get("video_description")
			video_path = request.FILES['video']

			video = Video(title=video_title, tags=video_tags, description=video_description,
	        			path=video_path, profile=video_profile, views=0, rates_count=0, rates_sum=0)

			video.save()
			video.generic_path = video.path.url.split('.')[-2]
			video.save()
			video_encode.delay(video.path.url)
			return redirect('video', video.slug)
		except:
			return render(request, '500.html', {'error': "El nombre del video ya existe"})
	else:
		return render(request, '500.html')


	
#										PUBLIC COMMENT VIEW
##########################################################################################
@csrf_exempt
def public_comment_view(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		user = get_object_or_404(User, username=username)
		comment_profile = Profile.objects.get(user=user)

		video = request.POST.get('video')
		comment_video = Video.objects.get(slug=video)

		comment = request.POST.get('comment')

		new_comment = Comment(video=comment_video, profile=comment_profile, comment=comment)
		new_comment.save()

		if comment_profile.profile_picture:
			profile_picture = comment_profile.profile_picture.url
		else:
			profile_picture = '/static/img/20.png' #Default Profile picture
		
		data = {
			'username': username,
			'video': video,
			'comment': comment,
			'published': new_comment.published,
			'profile_picture': profile_picture
		}
		return JsonResponse(data)
	else:
		return redirect(request.META.get('HTTP_REFERER'))
		

	
#										RATE VIEW
##########################################################################################
@csrf_exempt
def rate_view(request):
	if request.method == "POST":
		username = request.POST.get('username')
		user = get_object_or_404(User, username=username)
		rate_profile = Profile.objects.get(user=user)

		video = request.POST.get('video')
		rate_video = get_object_or_404(Video, slug=video)

		score = request.POST.get('rate')

		is_valored = False

		rates = Rate.objects.filter(video=rate_video)
		for rate in rates:
			if rate.profile == rate_profile:
				is_valored = True


		if is_valored == False:
			rate = Rate(video=rate_video, profile=rate_profile, score=score)
			rate.save()

			rate_video.rates_count += int(1)
			rate_video.rates_sum += int(score)
			rate_video.save()

			rates_average = rate_video.rates_sum/rate_video.rates_count


			data = { 'average': rates_average }
		else:
			data = { 'average': is_valored }

		return JsonResponse(data)
	else:
		return redirect(request.META.get('HTTP_REFERER'))


	
#										VIDEO VIEW
##########################################################################################
def video_view(request, video_slug):
	video = get_object_or_404(Video, slug=video_slug)
	video.views += 1
	video.save()

	comments = video.video_comments.all()
	if video.rates_sum != 0:
		rate_average = video.rates_sum/video.rates_count
	else:
		rate_average = 0
	context = {'video' : video, 'comments' : comments, 'rate_average': rate_average}
	return render(request, 'video.html', context)


	
#										CHANNEL VIEW
##########################################################################################
@login_required(login_url='/')
def channel_view(request, username_slug, tab='profile'):
	user = get_object_or_404(User, username=username_slug)
	profile = get_object_or_404(Profile, user=user)
	profile_videos = profile.videos.all()
	profile_video_rates = profile.profile_rates.all()
	context = { 'profile': profile, 'tab': tab, 'profile_videos': profile_videos,
				'video_rates': profile_video_rates }
	return render(request, 'channel.html', context)