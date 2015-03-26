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
// http://dumpk.com/2013/06/02/how-to-create-infinite-scroll-with-ajax-on-jquery/
function element_in_scroll(elem)
{
    var docViewTop = $('.three-column-day').scrollTop();
    var docViewBottom = docViewTop + $('.three-column-day').height();

    var elemTop = $(elem).offset().top;
    var elemBottom = elemTop + $(elem).height();

    return ((elemBottom <= docViewBottom) && (elemTop >= docViewTop));

}

$('.three-column-day').on('scroll', function(elem){
    if($(this).scrollTop() + $(this).innerHeight() >= this.scrollHeight) {
//    if (element_in_scroll(".three-column-day li:last")) {
      $(this).unbind('scroll');
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
//    $(this).bind('scroll');
});