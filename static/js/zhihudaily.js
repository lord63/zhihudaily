$('.three-column-day li a').on('click', function(event) {
  event.preventDefault();
  $.getJSON($(this).attr('href'), function(resp) {
    $('.three-column-title li').remove();
    var titles = resp.titles;
    for (var i = 0; i < titles.length; i++) {
      $('.three-column-title').append('<li>' + titles[i] + '</li>');
    }
  });
  $('.three-column-title').animate({scrollTop: 0}, 1000);
});