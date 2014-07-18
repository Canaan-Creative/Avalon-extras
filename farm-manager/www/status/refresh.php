<?php

//error_reporting(E_ALL);

system("./refresh.sh");
$msg = time();
echo json_encode(array('status'=>'2','msg'=>'刷新需要耗费很长时间，几分钟后请重新刷新页面'.$msg));exit;

