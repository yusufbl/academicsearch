document.addEventListener("DOMContentLoaded", function() {
    var downloadPDFLink = document.getElementById("downloadPDF");

    if (downloadPDFLink) {
        downloadPDFLink.addEventListener("click", function(event) {
            event.preventDefault(); // Sayfanın yeniden yüklenmesini engelle

            var articleToolbarLink = downloadPDFLink.getAttribute("data-pdf-url");

            // Dergipark URL'si ile article_toolbar_link'i birleştir
            var pdfUrl = "https://dergipark.org.tr" + articleToolbarLink;

            // PDF dosyasını yeni bir sekmede aç
            window.open(pdfUrl, '_blank');
        });
    }
});

