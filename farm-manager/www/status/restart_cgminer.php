<?php

//error_reporting(E_ALL);

$ip = empty($_POST['ip']) ? 0 : $_POST['ip'];
$port = empty($_POST['port']) ? 0 : $_POST['port'];

if((!$ip) || (!$port)){
	echo json_encode(array('status'=>'0','msg'=>'ip or port is null'));exit;
}

system("python restart_cgminer.py " . $ip . " " . join(' ' , explode(',',$port)));
$msg = time();
echo json_encode(array('status'=>'2','msg'=>'重启所有需要耗费很长时间，几分钟后请重新刷新页面'.$msg));exit;

