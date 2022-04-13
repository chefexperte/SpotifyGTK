#!/usr/bin/php-cgi

<?php
if(!empty($_POST['token'])){
$token = $_POST['token'];
$expire = $_POST['expiration'];
$refresh = $_POST['refresh_token'];
$file = fopen("../token.txt", 'w');
$expire_secs = time() + (int) $expire;
fwrite($file, $token . "\n" . $expire_secs . "\n" . $refresh);
fclose($file);
}else{
$file = fopen("../no_data_given.txt", 'w');
fwrite($file, "\$_POST data: ");
fwrite($file, file_get_contents('php://input'));
foreach($_POST as $item) {
fwrite($file, $item);
}
fclose($file);
}
?>