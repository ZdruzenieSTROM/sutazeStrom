function close_this(id) {
    elem = document.getElementById(id);

    elem.style.display = "none";
}

var input = document.getElementById("barcode_input"),
focuser = function () {
    input.focus();
};

focuser();
input.onblur = function () {
    setTimeout(focuser, 0);
};
