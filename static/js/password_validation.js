function checkPass()
{
    var pass1 = document.getElementById('password');
    var pass2 = document.getElementById('pass2');
    var message = document.getElementById('error-nwl');
    var goodColor = "#66cc66";
    var badColor = "#ff6666";

    if(pass1.value.length > 5)
    {
        pass1.style.backgroundColor = goodColor;
        message.style.color = goodColor;
        message.innerHTML = "character number ok!"
    }
    else
    {
        pass1.style.backgroundColor = badColor;
        message.style.color = badColor;
        message.innerHTML = " you have to enter at least 6 digit!"
        return;
    }

    if(pass1.value == pass2.value)
    {
        pass2.style.backgroundColor = goodColor;
        message.style.color = goodColor;
        message.innerHTML = "ok!"
    }
	else
    {
        pass2.style.backgroundColor = badColor;
        message.style.color = badColor;
        message.innerHTML = " These passwords don't match"
    }
}