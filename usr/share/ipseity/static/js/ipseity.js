/* Copyright (C) 2013-2014 Pieter E Sartain
 *
 * Progressive enhancements for Ipseity.
 *
 *
 */

$( document ).ready(function() {

  // The NFC interface doesn't actually reload the
  // interface, so we run a 2s reload loop.
  // Except for the edit window, when we don't ...
  var path = window.location.pathname.split("/");
  if (path.pop() != 'edit') {
    window.setInterval(function() {
      $("div#content").load("?ajax=true", function() {
        fixFormSubmit();
      });
    }, 2000);
  }

  fixFormSubmit();

});

function fixFormSubmit() {
  // Hook the form submit to pushing on the card itself.
  $('div#content > div:not(#add-new-person)').each(function() {

    var self = $(this);
    var form = self.children('form');

    // Hide the form buttons when using JS
    form.hide();

    // Mouse over the cards should provide a hand
    self.hover(function() {
        self.css('cursor','pointer');
    }, function() {
        self.css('cursor','default');
    });

    // And clicking the card should trigger the toggle
    self.click(function(event) {
      $.ajax({
        type: form.attr('method'),
        url: form.attr('action'),
        data: form.serialize(), // serializes the form's elements.
        success: function(data)
        {
          self.toggleClass("logged_in logged_out");
        }
      });
    }); // click

  }); // each card
}
