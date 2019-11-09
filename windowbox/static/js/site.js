$(document).ready(function() {
    handleTimeDisplay();
});

$(window).load(function() {
    if ($('#single-post').length > 0) handleSinglePost();
    if ($('#metadata').length > 0) handleMetadata();
});

function handleTimeDisplay() {
    $('time').each(function() {
        var $this  = $(this),
            elDate = new Date($this.attr('datetime')),
            date, time;

        if (!isNaN(elDate)) {
            // Mainly using this for the side-effect of converting to local TZ
            date = elDate.toLocaleString('en-US', {month: 'long', day: 'numeric', year: 'numeric'});
            time = elDate.toLocaleString('en-US', {hour: 'numeric', minute: '2-digit', timeZoneName: 'short'});
            $this.text(date + ' at ' + time);
        }
    });
}

function handleSinglePost() {
    var $attachment = $('#attachment'),
        $arrowNewer = $('.arrow.newer'),
        $arrowOlder = $('.arrow.older'),
        arrowHeight = ($arrowNewer.height() || $arrowOlder.height()),
        xPosIn      = ($arrowNewer.css('left') || $arrowOlder.css('right')),
        xPosOut     = -($arrowNewer.width() || $arrowOlder.width());

    $arrowNewer.css('left', xPosOut);
    $arrowOlder.css('right', xPosOut);

    // Sorta broke with jQuery 3.0.0 in IE9; don't have time to shave this yak.
    // (If page loads with mouse over image, "hover on" doesn't fire.)
    $attachment.hover(function() {
        $arrowNewer.stop().animate({left: xPosIn});
        $arrowOlder.stop().animate({right: xPosIn});
    }, function() {
        $arrowNewer.stop().animate({left: xPosOut});
        $arrowOlder.stop().animate({right: xPosOut});
    });

    function _positionArrows() {
        var arrowTop = ($attachment.height() - arrowHeight) / 2;

        $arrowNewer.css('top', arrowTop);
        $arrowOlder.css('top', arrowTop);

        // This garbage is needed because imagesLoaded doesn't support srcset
        setTimeout(_positionArrows, 1000);
    }

    $attachment.imagesLoaded(_positionArrows);
}

function handleMetadata() {
    var $metadata   = $('#metadata'),
        $pullTab    = $metadata.find('.pull-tab'),
        $scrollWrap = $metadata.find('.scroll-wrap'),
        $parent     = $metadata.parent(),
        openPos     = 0,
        inPos       = -($metadata.width() + 10),  //include 10px of box-shadow
        outPos      = inPos - $pullTab.outerWidth(),
        isOpen      = false;

    $metadata.css('right', outPos);

    $parent.hover(function() {
        if (!isOpen) {
            $metadata.stop().animate({right: inPos});
        }
    }, function() {
        if (!isOpen) {
            $metadata.stop().animate({right: outPos});
        }
    });

    $pullTab.click(function() {
        isOpen = !isOpen;

        if (isOpen) {
            $scrollWrap.css('height', $parent.height());

            $metadata.stop().animate({right: openPos});
        } else {
            $metadata.stop().animate({right: inPos});
        }
    });
}
