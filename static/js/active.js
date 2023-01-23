$(document).ready(function () {
    $('.header-carousal').owlCarousel({
        items: 1,
        loop: true,
        autoplay: true,
        autoplayTimeout: 5000,
        margin: 10,
        nav: true,
        navText: [
            "<i class=\"fa fa-angle-left\" aria-hidden=\"true\"></i>",
            "<i class=\"fa fa-angle-right\" aria-hidden=\"true\"></i>"],
        merge: true,
    });
    $('.testimonial-carousal-one').owlCarousel({
        items: 1,
        loop: true,
        autoplay: true,
        autoplayTimeout: 5000,
        margin: 10,
        nav: true,
        navText: [
            "<i class=\"fa fa-angle-left\" aria-hidden=\"true\"></i>",
            "<i class=\"fa fa-angle-right\" aria-hidden=\"true\"></i>"],
        merge: true,
    });
    $('.blog-carousal').owlCarousel({
        items: 1,
        loop: true,
        autoplay: true,
        autoplayTimeout: 5000,
        margin: 10,
        nav: true,
        navText: [
            "<i class=\"fa fa-angle-left\" aria-hidden=\"true\"></i>",
            "<i class=\"fa fa-angle-right\" aria-hidden=\"true\"></i>"],
        merge: true,
    });
    $('.footer-carousal').owlCarousel({
        items: 4,
        loop: true,
        autoplay: true,
        autoplayTimeout: 3000,
        margin: 10,
        nav: true,
        navText: [
            "<i class=\"fa fa-angle-left\" aria-hidden=\"true\"></i>",
            "<i class=\"fa fa-angle-right\" aria-hidden=\"true\"></i>"],
        merge: true,
        responsive: {
            0: {
                items: 2
            },
            450: {
                items: 3
            },
            580: {
                items: 4
            },
            1000: {
                items: 4
            }
        }
    });


    var $grid = $('.grid').isotope({
        itemSelector: '.portfolio-item',
        layoutMode: 'fitRows'
    });
    var filterFns = {
        numberGreaterThan50: function () {
            var number = $(this).find('.number').text();
            return parseInt(number, 10) > 50;
        },
        ium: function () {
            var name = $(this).find('.name').text();
            return name.match(/ium$/);
        }
    };
    $('.filters-button-group').on('click', 'button', function () {
        var filterValue = $(this).attr('data-filter');
        filterValue = filterFns[filterValue] || filterValue;
        $grid.isotope({
            filter: filterValue
        });
    });
    $('.button-group').each(function (i, buttonGroup) {
        var $buttonGroup = $(buttonGroup);
        $buttonGroup.on('click', 'button', function () {
            $buttonGroup.find('.is-checked').removeClass('is-checked');
            $(this).addClass('is-checked');
        });
    });


    $('.portfolio-item').magnificPopup({
        delegate: 'a',
        type: 'image',
        closeOnContentClick: false,
        closeBtnInside: false,
        mainClass: 'mfp-with-zoom mfp-img-mobile',
        image: {
            verticalFit: true,
        },
        gallery: {
            enabled: true
        },
    });


    $(".one1").click(function () {
        $(".two1").css("display", "block").siblings(".tom").css("display", "none")
    });


    $(".one2").click(function () {
        $(".two2").css("display", "block").siblings(".tom").css("display", "none");
    });


    $(".one3").click(function () {
        $(".two3").css("display", "block").siblings(".tom").css("display", "none");
    });


    $(".one4").click(function () {
        $(".two4").css("display", "block").siblings(".tom").css("display", "none");
    });
});