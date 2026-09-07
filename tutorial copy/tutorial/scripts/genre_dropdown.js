let jsonData;
$.getJSON("../games.json", function(json) {
    jsonData = json; // this will show the info it in firebug console
});

function createGenreDropdown(jsonData){
    let loc = document.getElementById("genre_dropdown");
    const tags = jsonData[0].tags
    for(let key in tags) {
        let option = document.createElement("option");
        option.textContent = key;
        option.value = tags[key];
        loc.append(option);
    }
}

createGenreDropdown(jsonData);