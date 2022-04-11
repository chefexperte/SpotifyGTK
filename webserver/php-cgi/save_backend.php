#!/usr/bin/php-cgi

<?php
if(!empty($_POST['data'])){
$data = $_POST['data'];
$file = fopen("token.txt", 'w');//creates new file
fwrite($file, $data);
fclose($file);
}else{
$file = fopen("no_data_given.txt", 'w');//creates new file
fwrite($file, "\$_POST data: ");
fwrite($file, file_get_contents('php://input'));
foreach($_POST as $item) {
fwrite($file, $item);
}
fclose($file);
}
?>