#!/usr/bin/php-cgi

<?php
if(!empty($_POST['token'])){
$token = $_POST['token'];
$expire = $_POST['expiration'];
$refresh = $_POST['refresh_token'];
$file = fopen("../token.txt", 'w');
$seven_days = 60*60*24*7;
$expire_secs = 0;
if ($expire > $seven_days) {
    $expire_secs = (int) $expire;
} else {
    $expire_secs = time() + (int) $expire;
}

echo "time(): " . time() . "\n";
echo "\$expire: $expire\n";
echo "\$expire_secs: $expire_secs\n";
fwrite($file, $token . "\n" . $expire_secs . "\n" . $refresh . "\n");
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