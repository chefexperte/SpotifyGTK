#!/usr/bin/php-cgi

<?php
// Replace with your app's client ID, redirect URI and desired scopes
if (file_exists("../client-auth.txt")) {
    $file = file("../client-auth.txt");
    $clientId = substr($file[0], 0, -1);
    $clientSecret = substr($file[1], 0, -1);
    echo "const clientId = '".$clientId."';\n";
    echo "const clientSecret = '".$clientSecret."';\n";
}

echo "time_now = ".time().";\n";
if (file_exists("../token.txt")) {
    $file = file("../token.txt");
    $time_now = time();
    $expire_time = (int) substr($file[1], 0, -1);
    $refresh_token = substr($file[2], 0, -1);
    $token = substr($file[0], 0, -1);
    if ($expire_time > $time_now) {
        echo "_token = \"".$token."\";\n";
        echo "_expire = \"".$expire_time."\";\n";
        echo "_refresh = \"".$refresh_token."\";\n";
    } else {
        echo "_refresh = \"".$refresh_token."\";\n";
        echo "request_refresh = true;";
    }
    //echo $expire_time . "-" . $time_now . " = " . $expire_time-$time_now;
}
?>