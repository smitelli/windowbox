'use strict';

var $ = require('jquery');

module.exports = function () {
    var $arrowPrev = $('.arrow.previous'),
        $arrowNext = $('.arrow.next'),
        inPos      = $arrowPrev.css('left'),
        outPos     = -$arrowPrev.width();

    $arrowPrev.css('left', outPos);
    $arrowNext.css('right', outPos);

    $('#attachment').hover(function () {
        $arrowPrev.stop().animate({ left  : inPos });
        $arrowNext.stop().animate({ right : inPos });
    }, function () {
        $arrowPrev.stop().animate({ left  : outPos });
        $arrowNext.stop().animate({ right : outPos });
    });
};
