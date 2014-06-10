'use strict';

var $         = require('jquery'),
    imgLoaded = require('image-loaded');

module.exports = function () {
    var $attachment = $('#attachment'),
        $arrowPrev  = $('.arrow.previous'),
        $arrowNext  = $('.arrow.next'),
        inPos       = ($arrowPrev.css('left') || $arrowNext.css('right')),
        outPos      = -($arrowPrev.width() || $arrowNext.width());

    $attachment.find('img').each(function () {
        imgLoaded(this, function () {
            var middleTop = ($attachment.height() / 2) - ($('.arrow').innerHeight() / 2);

            $arrowPrev.css('top', middleTop);
            $arrowNext.css('top', middleTop);
        });
    });

    $arrowPrev.css('left',  outPos);
    $arrowNext.css('right', outPos);

    $attachment.hover(function () {
        $arrowPrev.stop().animate({ left  : inPos });
        $arrowNext.stop().animate({ right : inPos });
    }, function () {
        $arrowPrev.stop().animate({ left  : outPos });
        $arrowNext.stop().animate({ right : outPos });
    });
};
