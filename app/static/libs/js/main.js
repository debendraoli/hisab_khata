let csrftoken = $('meta[name=csrf-token]').attr('content');
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)}},
});
jQuery(document).ready(function($) {
    'use strict';

    // ============================================================== 
    // Notification list
    // ============================================================== 
    if ($(".notification-list").length) {

        $('.notification-list').slimScroll({
            height: '250px'
        });

    }

    // ============================================================== 
    // Menu Slim Scroll List
    // ============================================================== 


    if ($(".menu-list").length) {
        $('.menu-list').slimScroll({

        });
    }

    // ============================================================== 
    // Sidebar scrollnavigation 
    // ============================================================== 

    if ($(".sidebar-nav-fixed a").length) {
        $('.sidebar-nav-fixed a')
            // Remove links that don't actually link to anything

            .click(function(event) {
                // On-page links
                if (
                    location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') &&
                    location.hostname == this.hostname
                ) {
                    // Figure out element to scroll to
                    var target = $(this.hash);
                    target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
                    // Does a scroll target exist?
                    if (target.length) {
                        // Only prevent default if animation is actually gonna happen
                        event.preventDefault();
                        $('html, body').animate({
                            scrollTop: target.offset().top - 90
                        }, 1000, function() {
                            // Callback after animation
                            // Must change focus!
                            var $target = $(target);
                            $target.focus();
                            if ($target.is(":focus")) { // Checking if the target was focused
                                return false;
                            } else {
                                $target.attr('tabindex', '-1'); // Adding tabindex for elements not focusable
                                $target.focus(); // Set focus again
                            }
                        });
                    }
                }
                $('.sidebar-nav-fixed a').each(function() {
                    $(this).removeClass('active');
                })
                $(this).addClass('active');
            });

    }

    // ============================================================== 
    // tooltip
    // ============================================================== 
    if ($('[data-toggle="tooltip"]').length) {
            
            $('[data-toggle="tooltip"]').tooltip()

        }

     // ============================================================== 
    // popover
    // ============================================================== 
       if ($('[data-toggle="popover"]').length) {
            $('[data-toggle="popover"]').popover()

    }
     // ============================================================== 
    // Chat List Slim Scroll
    // ============================================================== 
        

        if ($('.chat-list').length) {
            $('.chat-list').slimScroll({
            color: 'false',
            width: '100%'


        });
    }

        $(function () {
		$('#delay-modal').on('show.bs.modal', function () {
			var myModal = $(this);
			clearTimeout(myModal.data('hideInterval'));
			myModal.data('hideInterval', setTimeout(function () {
				myModal.modal('hide');
			}, 2500));
		});
	});

        Noty.overrideDefaults({
            type   : 'notification',
            layout   : 'topRight',
            theme    : 'bootstrap-v4',
            closeWith: ['click', 'button'],
            animation: {
                open : 'animated bounceInRight',
                close: 'animated bounceOutRight'
            },
            sounds: {
                sources: ['../sound/plucky.mp3'],
                volume: 1,
            }
        });
        $.extend($.fn.dataTable.defaults, {
            lengthChange: false,
            responsive: true,
            buttons: ['copy', 'excel', 'pdf', 'print', 'colvis'],
            processing: true,
            Sort: true,
            autoWidth: false,
            serverSide: true,
            ajax: {
                type: 'POST',
                dataType: 'json',
            },
            "lengthMenu": [
                [10, 15, 20, -1],
                [10, 15, 20, "All"]
            ],


        });

});
