'use strict';

var $         = require('jquery'),
    imgLoaded = require('image-loaded');

module.exports = function () {
    var $metadata   = $('#metadata'),
        $pullTab    = $metadata.find('.pull-tab'),
        $scrollWrap = $metadata.find('.scroll-wrap'),
        $parent     = $metadata.parent(),
        openPos     = 0,
        inPos       = -($metadata.width() + 10),  //include 10px of box-shadow
        outPos      = inPos - $pullTab.outerWidth(),
        isOpen      = false;

    $metadata.css('right', outPos);

    $parent.find('img').each(function () {
        imgLoaded(this, function () {
            $scrollWrap.css('height', $parent.height());
        });
    });

    $parent.hover(function () {
        if (!isOpen) {
            $metadata.stop().animate({ right : inPos });
        }
    }, function () {
        if (!isOpen) {
            $metadata.stop().animate({ right : outPos });
        }
    });

    $pullTab.click(function () {
        isOpen = !isOpen;

        if (isOpen) {
            $metadata.stop().animate({ right : openPos });
        } else {
            $metadata.stop().animate({ right : inPos });
        }
    });
};
