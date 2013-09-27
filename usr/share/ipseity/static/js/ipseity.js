$( document ).ready(function() {

  var path = window.location.pathname.split("/");
  if (path.pop() != 'edit') {
    window.setInterval(function() {
      $("div#content").load("?ajax=true");
    }, 2000);
  }

});