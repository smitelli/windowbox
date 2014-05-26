'use strict';

var $         = require('jquery'),
    imgLoaded = require('image-loaded');

module.exports = function () {
    var $metadata = $('#metadata'),
        $parent   = $metadata.parent();

    $parent.find('img').each(function () {
        imgLoaded(this, function () {
            $metadata.css('height', $parent.height());
        });
    });
};
