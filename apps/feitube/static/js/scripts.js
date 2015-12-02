//Conectar cliente con servidor
var socket = io.connect('http://localhost:9998', { 'forceNew': true });
//
//
/********Refresh del frontend para todos los usuarios (comentarios y valoraciones)*********/
socket.on('comments', function(data){
	renderComments(data);
})

socket.on('rates', function(data){
	if (data.average != true) { //Si no ha valorado el video
		renderRates(data);
	}
});

function renderRates(data){
	var truncated_average = Math.floor(data.average * 10) / 10;
	document.getElementById('rate_average').innerHTML = truncated_average;
}

//Añade un elemento <li> a la lista de comentarios
function renderComments(data){
	var html = `<img class="col s4 m2 responsive-img circle" src='${data.profile_picture}' alt="picture">
				<div class="col s8 m10">
					<div class="row">
						<p class="col s12 m4">${data.username}</p>
						<p class="col s12 m8">Publicado el ${data.published}</p>
					</div>
				</div>
				<blockquote class="comment col s12">
					${data.comment}
				</blockquote>`;

	var parentGuest = document.getElementById("messages"); 
	var childGuest = document.createElement("li"); 
	childGuest.class = "row section"; 
	childGuest.innerHTML = html; 
	if (data.username != undefined) {
		parentGuest.parentNode.appendChild(childGuest);
	}else{
		alert(data.comment);
	};
}

//////////////////////////////////////////////////////////////////////
// 		
//
/********Refresh del frontend para el usuario que comentó o valoró*********/
socket.on('showToast', function(data){
	if (data.average == true) {
		Materialize.toast("You can't rate a video twice", 3000, 'rounded');
	}else{
		Materialize.toast('Thanks for rating', 3000, 'rounded');
	};
});

socket.on('refreshCommentField', function(){
	document.getElementById('comment_body').value = '';
});
//////////////////////////////////////////////////////////////////////
//
//
/********Eventos de comentarios y valoraciones*********/
$('#comment_form').on('submit', function(e){
	var data = {
		username: document.getElementById('user_picture').getAttribute('alt'),
		video: document.getElementById('video-container').getAttribute('name'),
		comment: document.getElementById('comment_body').value
	};
	socket.emit('new-comment', data);
	return false;	
});

$('.formValidation').bind('keypress', function (event) {
    var regex = new RegExp("^[a-zA-Z0-9_., \b/\t/g]+$");
    var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
    if (!regex.test(key)) {
       event.preventDefault();
       return false;
    }
});


$('.grade').on('click', function(e){
	var data = {
		username: document.getElementById('user_picture').getAttribute('alt'),
		video: document.getElementById('video-container').getAttribute('name'),
		rate: this.children[0].innerHTML
	};
	socket.emit('new-rate', data);
	return false;
});

document.getElementById('embed_code').addEventListener('click', function(){
	var video_slug = document.getElementById('video-container').getAttribute('name');
	alert(`Copie el siguiente contenido para incrustar el video en su sitio:\n\n<div style="overflow: hidden;"><iframe style="border: 0px none; padding: 0; margin-left: -11px; height: 395px; margin-top: -75px; margin-bottom: -5px; width: 540px;" scrolling="no" src="http://localhost:8000/watch/${video_slug}" frameborder="0" allowfullscreen></iframe></div>`);
});
//////////////////////////////////////////////////////////////////////
//
//
/********Eventos jQuery para el SideBar y los modal de Login y Registro*********/
$('.modal-trigger').leanModal();

// Initialize collapse button
$('.button-collapse').sideNav({
		menuWidth: 240, // Default is 240
		edge: 'left', // Choose the horizontal origin
		//closeOnClick: true // Closes side-nav on <a> clicks, useful for Angular/Meteor
	}
);
//////////////////////////////////////////////////////////////////////
//
//
/********Feed de twitter*********/
!function(d,s,id){
	var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';
	if(!d.getElementById(id)){
		js=d.createElement(s);
		js.id=id;
		js.src=p+"://platform.twitter.com/widgets.js";
		fjs.parentNode.insertBefore(js,fjs);
	}
}(document,"script","twitter-wjs");

//////////////////////////////////////////////////////////////////////////////////////////////