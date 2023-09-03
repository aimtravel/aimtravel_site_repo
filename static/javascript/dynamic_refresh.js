function attachPaginationHandlers() {
    $(".pagination a").on("click", function (e) {
        e.preventDefault();
        console.log("Link clicked: " + $(this).attr("href")); // Log the clicked URL
        var pageUrl = $(this).attr("href");
        var slideOffersContent = $('.offer-slides').html();
        var paginator = $('.pagination').html();
        console.log("data:", slideOffersContent);
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
                var newPage = $(data).find('.pagination').html();
                console.log("AJAX success:", newContent);
                $(".offer-slides").html(newContent);
                $(".pagination").html(newPage);

                // Scroll to the top of .offer-slides
                var topOfOfferSlides = $("#offers-page-top-row").offset().top;
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