document.addEventListener("DOMContentLoaded", function() {
    
    var selectors = document.querySelectorAll("#list-selector, #filter-selector");
    selectors.forEach(function(selector) {
        selector.addEventListener("change", function() {
            
            var allLists = document.querySelectorAll(".list-container");
            for (var i = 0; i < allLists.length; i++) {
                allLists[i].style.display = "none";
            }

            
            var selectedValue = this.value;
            var selectedList = document.getElementById(selectedValue);
            if (selectedList) {
                selectedList.style.display = "block";
            }
        });
    });

    
    document.getElementById("list-selector").dispatchEvent(new Event('change'));

    
    document.getElementById("filter-selector").addEventListener("change", function() {
        var selectedValue = this.value;
        if (selectedValue === "ortak_yayinlar_liste") {
            
            var allLists = document.querySelectorAll(".list-container");
            for (var i = 0; i < allLists.length; i++) {
                allLists[i].style.display = "none";
            }
            
            var selectedList = document.getElementById(selectedValue);
            if (selectedList) {
                selectedList.style.display = "block";
            }
        }
    });
});
