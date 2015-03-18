$('.three-column-day li a').on('click', function(event) {
  event.preventDefault();
  $.getJSON($(this).attr('href'), function(resp) {
    $('.three-column-title li').remove();
    var news = resp.news;
    for (var i = 0; i < news.length; i++) {
      $('.three-column-title').append('<li><a href="' + news[i]['url'] + '">'+ news[i]['title'] + '</a></li>');
    }
  });
  $('.three-column-title').animate({scrollTop: 0}, 1000);
});