// For the scroll effects.
stroll.bind('.stroll-list ul', {live: true});


// Click 'more' then append days.
$('.load').on('click', function(){
  var last = $('.three-column-day li a').eq(-1).html();
  $.ajax('/three-columns/append-date/' + last, {
    type: 'GET',
    dataType: 'json',
    success: function(resp){
      resp.append_list.map(function(date) {
        $('.load').before("<li><a href='/three-columns/" + date + "' class='days'>" + date + "</a></li>");
      });
    }
  });
});


// Click the date and show the news titles.
// Event binding on dynamically elements：
// https://stackoverflow.com/a/6658774 and https://stackoverflow.com/a/1207393
$('.three-column-day').on('click', 'a.days', function(event) {
  event.preventDefault();
  $.getJSON($(this).attr('href'), function(resp) {
    $('.three-column-title li').remove();
    // https://goo.gl/fRKpMD
    var news = resp.news;
    var textToInsert = [];
    var length = news.length;
    var i = 0;
    for (var a = 0; a < length; a += 1) {
//      textToInsert[i++] = '<li><a href="https://news-at.zhihu.com/api/4/news/';
      textToInsert[i++] = '<li><a href="/three-columns/contents/';
      textToInsert[i++] = news[a]['id'];
      textToInsert[i++] = '" class="titles">';
      textToInsert[i++] = news[a]['title'];
      textToInsert[i++] = '</a></li>';
    }
    $('.three-column-title').append(textToInsert.join(''));
  });
  $('.three-column-title').animate({scrollTop: 0}, 1000);
});


// Mark clicked days in the first column.
$('.stroll-list').on('click', 'a', function() {
  $(this).css( "color", "#acacc6");
});


// Click the title and show the content.
$('.three-column-title').on('click', 'a.titles', function(event) {
  event.preventDefault();
    $.ajax($(this).attr('href'), {
      type: 'GET',
      dataType: 'json',
      success: function(resp){
          $('.three-column-content .main-wrap').replaceWith(resp['body']);
      },
      beforeSend: function() {$(".three-column-content").isLoading({text: "Loading", position: "overlay"});},
      complete: function() {$(".three-column-content").isLoading( "hide" );}
    });
  $('.three-column-content').animate({scrollTop: 0}, 1000);
});
