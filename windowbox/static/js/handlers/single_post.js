'use strict';

var $ = require('jquery');

module.exports = function () {
    var inPos  = $('.arrow.previous').css('left'),
        outPos = -$('.arrow.previous').width();

    $('.arrow.previous').css('left', outPos);
    $('.arrow.next').css('right', outPos);

    $('#attachment').hover(function () {
        $('.arrow').stop();
        $('.arrow.previous').animate({ left : inPos });
        $('.arrow.next').animate({ right : inPos });
    }, function () {
        $('.arrow').stop();
        $('.arrow.previous').animate({ left : outPos });
        $('.arrow.next').animate({ right : outPos });
    });
};
