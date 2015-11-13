$(document).ready(function() {
	console.log("oh god");
	var tags = window.tags;
	
	$(".tag").each(function(){
		$(this).click(function(e){
			var tag = $(this).attr('id');
			console.log($(this).attr('id'));
			if(tags.indexOf(tag) < 0) {
				tags.push(tag);
				$(this).toggleClass('mdl-button--accent mdl-button--primary');
				$(this).addClass('selected-tag');
			}
			else {
				tags.splice(tags.indexOf(tag), 1);
				$(this).toggleClass('mdl-button--primary mdl-button--accent');
				$(this).removeClass('selected-tag');
			}
			console.log(tags)
		});
	})

	$("#tagSubmit").click(function(e){
		console.log("sending");
		console.log(JSON.stringify(tags));
		$.post('/profile', {'tag': JSON.stringify(tags)});
	});
});