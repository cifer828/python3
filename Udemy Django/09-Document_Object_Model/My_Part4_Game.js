var block = document.querySelectorAll("div[class = 'container'] td");


for (var i = 0; i < block.length; i++){
    var b = block[i];
    b.addEventListener("click", function () {
        if (this.textContent === '')
            this.textContent = 'X';
        else if (this.textContent === 'X')
            this.textContent = 'O';
        else if (b.textContent === 'O')
            this.textContent = '';
    });
}

var btn = document.querySelector("#b");

btn.addEventListener('click', function () {
    for (var i = 0; i < block.length; i++){
        block[i].textContent = '';
    }
});