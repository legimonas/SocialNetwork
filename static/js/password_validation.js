function checkPass() {
    var pass1 = document.getElementById('password');
    var pass2 = document.getElementById('pass2');
    var message = document.getElementById('error-nwl');
    var goodColor = "#FFFFFF";
    var badColor = "#F46670";

    if(pass1.value.length > 5) {
        pass1.style.borderColor = goodColor;
        pass1.style.borderWidth = "0px";
        message.style.color = goodColor;
        message.innerHTML = "";
    }
    else {
        pass1.style.borderColor = badColor;
        pass1.style.borderWidth = "1.5px";
        message.style.color = badColor;
        message.innerHTML = " you have to enter at least 6 digit!"
        return;
    }

    if(pass1.value === pass2.value) {
        pass2.style.borderColor = goodColor;
        pass1.style.borderWidth = "0px";
        message.style.color = goodColor;
        message.innerHTML = "";
    }
    else {
        pass2.style.borderColor = badColor;
        pass2.style.borderWidth = "1.5px";
        message.style.color = badColor;
        message.innerHTML = "These passwords don't match"
    }
}