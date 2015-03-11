<?php

require  'medoo.min.php';
require  'settings.php';

$headers = array(
'Content-Type:application/json',
'Authorization:key=AIzaSyDktZ4hsSv2SbwHPUhy22CJh2jcn81qdgw'
);

$database = new medoo([
	// required
	'database_type' => 'mysql',
	'database_name' => $DB_NAME,
	'server' => $DB_HOST,
	'username' => $DB_USERNAME,
	'password' => $DB_PASSWORD,
	'charset' => $DB_CHARSET,
 	'port' => 3306
]);
 

#Get Android Push Messages
$filter = ["AND" => ["processed" => false,"device_type" => 1], "LIMIT" => 100];
$datas = $database->select("controller_pushnotifications", "*",$filter);


foreach($datas as $msg){
	$arr   = array();
	$arr['data'] = json_decode($msg["contents"], true);
	$arr['registration_ids'] = array();
	$arr['registration_ids'][0] = $msg["device_id"];
	
	try{
		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL,    'https://android.googleapis.com/gcm/send');
		curl_setopt($ch, CURLOPT_HTTPHEADER,  $headers);
		curl_setopt($ch, CURLOPT_POST,    true);
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
		curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
		curl_setopt($ch, CURLOPT_POSTFIELDS,json_encode($arr));
		$response_json = curl_exec($ch);
		$response = json_decode($response_json, true);
		if($response["success"] == 1){
			//success
			$database->update("controller_pushnotifications",["processed" => true] ,["id" => $msg["id"]]);
		}else{
			//fail
		}
		curl_close($ch);
	} catch (Exception $e) {
    	//echo 'Caught exception: ',  $e->getMessage(), "\n";
	}
}

?>
