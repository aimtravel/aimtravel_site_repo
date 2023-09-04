function attachPaginationHandlers() {
    $("#offers-buttons a").on("click", function (e) {
        e.preventDefault();
        var pageUrl = $(this).attr("href");
        var slideOffersContent = $('.offer-slides').html();
        var paginator = $('#offers-buttons').html();
        console.log(pageUrl)

        $.ajax({
            url: pageUrl,
            type: "GET",
            dataType: "html",
            data: {
                slide_offers_content: slideOffersContent,
                paginator: paginator,
            },
            success: function (data) {

                var newContent = $(data).find('.offer-slides').html();
                var newPage = $(data).find('#offers-buttons').html();

                $(".offer-slides").html(newContent);
                $("#offers-buttons").html(newPage);

                // Scroll to the top of .offer-slides
                var topOfOfferSlides = $("#pagination-anchor").offset().top;
                $("html, body").animate({scrollTop: topOfOfferSlides}, 500); // Adjust the duration as needed


                attachPaginationHandlers();
            },
            error: function (xhr, status, error) {
                console.error("AJAX error", error);
            }
        });
    });
}

$(document).ready(function () {
    console.log("Document ready.");
    attachPaginationHandlers();
})