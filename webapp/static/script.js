function search() {
    var searchInput = document.getElementById('searchInput').value;
    var resultsDiv = document.getElementById('results');

    resultsDiv.innerHTML = '';

    for (var i = 0; i < 10; i++) {
        var resultHTML = '<div class="result">' +
                            '<h2><a href="#" onclick="goToArticle(' + i + ')">Örnek Makale Başlığı ' + (i + 1) + '</a></h2>' +
                         '</div>';

        resultsDiv.innerHTML += resultHTML;
    }
}

function goToArticle(articleId) {
    window.location.href = '/makale/' + articleId;


    alert("Makaleye yönlendirme işlemi burada gerçekleştirilecektir.");
}


