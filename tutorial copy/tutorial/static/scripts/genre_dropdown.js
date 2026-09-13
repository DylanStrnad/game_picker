let jsonData;
$.ajax({
    url: "/games_tags.json",
    dataType: "json",
    async: false,
    success: function(json) {
        jsonData = json;
        console.log("json loaded");
    }
});

function createGenreDropdown(jsonData){
    console.log("making dropdown")
    let loc = document.getElementById("genre_dropdown");
    const tags = jsonData[0].tags
    for(let key in tags) {
        let option = document.createElement("option");
        option.textContent = key;
        option.value = tags[key];
        console.log(option.textContent)
        loc.append(option);
    }
}

createGenreDropdown(jsonData);