var $ = require('jquery'),
    _ = require('lodash'),

    handlers = {
        '#single-post' : require('./handlers/single_post.js')
    };

$(function () {
    _(handlers).omit(function (handler, selector) {
        return $(selector).length === 0;
    }).forOwn(function (handler) {
        handler();
    });
});