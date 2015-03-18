$('.three-column-day li a').on('click', function(event) {
  event.preventDefault();
  $.getJSON($(this).attr('href'), function(resp) {
      console.log(resp.titles);
  });
});