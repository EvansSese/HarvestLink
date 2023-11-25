// password-validation.js
function validatePassword() {
    var password = document.getElementById("password").value;
    var confirmPassword = document.getElementById("confirmPassword").value;

    if (password !== confirmPassword) {
        alert("Password and Confirm Password do not match");
        return false;
    }

    return true;
}
