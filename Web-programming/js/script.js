var currTop;
var currLeft;

// monitor for the window scroll position
var headerChange = function(){

    var section1 = $(".navItem").eq(0);
    var section2 = $(".navItem").eq(1);
    var section3 = $(".navItem").eq(2);

    if($(window).scrollTop() != 0)
   {
       // if we are not at top, then shrink the navbar
       $("#navbar").removeClass('navSta');
       $("#navbar").addClass('navDyn');
       $(".navItem").each(function(){
           $(this).removeClass('hc')
           $(this).addClass('hcNew');
       });

       // code below highlights the item in the navigation bar
       // based on the current position on the page
       var headerHeight = 100;
       var loc = $(window).scrollTop();
       var sectionHeight = $("#section1").height();
       if(loc < headerHeight)
       {
           section1.removeClass('positionIndicator');
           section2.removeClass('positionIndicator');
           section3.removeClass('positionIndicator');
       }
       else if(loc < sectionHeight + headerHeight)
       {
           section1.addClass('positionIndicator');
           section2.removeClass('positionIndicator');
           section3.removeClass('positionIndicator');
       }

       else if(loc < 2*sectionHeight + headerHeight)
       {
           section1.removeClass('positionIndicator');
           section2.addClass('positionIndicator');
           section3.removeClass('positionIndicator');
       }

       else if(loc < 3*sectionHeight + headerHeight)
       {
           section1.removeClass('positionIndicator');
           section2.removeClass('positionIndicator');
           section3.addClass('positionIndicator');
       }
   }
    else{
        // if we are at top of page, revert the nav bar to original size
       $("#navbar").removeClass('navDyn');
       $("#navbar").addClass('navSta');
       $(".navItem").each(function(){
           $(this).removeClass('hcNew');
           $(this).addClass('hc');
       });

       section1.removeClass('positionIndicator');
       section2.removeClass('positionIndicator');
       section3.removeClass('positionIndicator');
   }
};

$(window).scroll(headerChange);

// function for smooth-scroll
$('#navbar ul li a').click(function(){
    $(window).unbind('scroll'); // unbind the scroll for the duration of this function call
    var target = $(this).attr('target');
    var targetOffset = $(target).offset().top;

    $('body, html')
        .animate({scrollTop: targetOffset}, 1000, 'swing', function(){
            $(window).scroll(headerChange);  // re-apply scroll monitoring
            headerChange();
        });
});

// handles the production of modal. Scrolling is inhibited when modal is open
$('#techSpecs').click(function(){
    $("#modal").css({'opacity':1,'z-index':99999});
    $("body").append("<div id='blurCover'></div>");
    $("#blurCover").css({'height':'100%', 'width':'100%', 'background-color':'#000000',
        'position':'fixed', 'top':0, 'left':0, 'opacity':0.4
    });

    // disable scrolling
    currTop = $(window).scrollTop();
    currLeft = $(window).scrollLeft();
    $(window).scroll(function(){
        $(this).scrollTop(currTop).scrollLeft(currLeft);
    });
});

// handles the closing of the modal. Scrolling is re-enabled
$("#closeIcon").click(function(){

    $("#modal").css({'opacity':0,'z-index':-1});
    $("#blurCover").remove();

    // restore scrolling
    $(window).unbind('scroll');
    $(window).scroll(headerChange);
});

// carousel index and number of images
var currIndex = 0;
var numItems = $("#carousel").children().length;

// initiate carousel
var carouselLauncher = function(){
    $('#carousel > li:eq(' + currIndex + ')').addClass('active');
};

// handles carousel next button
$(".next").click(function() {
    var currImage = $("#carousel > li.active");
    currIndex = (currIndex + 1)%numItems;
    currImage.removeClass('active');
    $('#carousel > li:eq(' + currIndex + ')').addClass('active');
});

// handles carousel previous button
$(".prev").click(function() {
    var currImage = $("#carousel > li.active");
    currIndex = currIndex - 1;
    if(currIndex == -1) {
        currIndex = numItems-1;
    }
    currImage.removeClass('active');
    $('#carousel > li:eq(' + currIndex + ')').addClass('active');
});

$(document).ready(carouselLauncher);
