<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $name = htmlspecialchars($_POST['name']);
    $email = htmlspecialchars($_POST['email']);
    $amount = htmlspecialchars($_POST['amount']);
    $payeer = htmlspecialchars($_POST['payeer']);

    $msg = "New Order:\nName: $name\nEmail: $email\nAmount: $amount\nPayeer: $payeer";
    mail("payeerexchange2@gmail.com", "New Payeer Order", $msg);

    echo "Order received! We will contact you soon.";
}
?>
