// Click the date and show the news titles.
$('.three-column-day').on('click', 'a.days', function(event) {
  event.preventDefault();
  $.getJSON($(this).attr('href'), function(resp) {
    $('.three-column-title li').remove();
    // http://goo.gl/fRKpMD
    var news = resp.news;
    var textToInsert = [];
    var length = news.length;
    var i = 0;
    for (var a = 0; a < length; a += 1) {
      textToInsert[i++] = '<li><a href="/three-columms/news/';
      textToInsert[i++] = news[a]['id'];
      textToInsert[i++] = '">';
      textToInsert[i++] = news[a]['title'];
      textToInsert[i++] = '</a></li>';
    }
    $('.three-column-title').append(textToInsert.join(''));
  });
  $('.three-column-title').animate({scrollTop: 0}, 1000);
});


// Infinite scroll for the first column.
$('.three-column-day').on('scroll', function(elem){
    // http://stackoverflow.com/a/6271466
    if($(this).scrollTop() + $(this).innerHeight() >= this.scrollHeight) {
      var last = $('.three-column-day li:last a').eq(0).html();
      $.ajax('/three-columns/append-date/' + last, {
        type: 'GET',
        dataType: 'json',
        success: function(resp){
          resp.append_list.map(function(date) {
            $('.three-column-day').append("<li><a href='/three-columns/" + date + "' class='days'>" + date + "</a></li>");
          });
        }
      });
    }
});