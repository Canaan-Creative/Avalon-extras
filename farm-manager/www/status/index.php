<?php
## T-map
$file = file_get_contents("json/farm.json");
$farm = json_decode($file,true);
$file = file_get_contents("json/status.json");
$status = json_decode($file,true);
$zones = $farm["zone"];
$zones2 = $status["zone"];
$farm_map = array();
$z = 0;
foreach($zones as $zone){
	$zone2 = $zones2[$z];
	$zone_map = array();
	$miner_per_table = $zone["layers"] * $zone["plot_split"];
	for($i = 0; $i < ceil( count($zone["miner"]) / $miner_per_table) ; $i ++) {
		$split_map = array();
		for($j = 0; $j < $zone["layers"]; $j ++) $split_map[] = array_fill(0, $zone["plot_split"], ' ');
		$zone_map[] = $split_map;
	}
	for($i=0; $i < count($zone["miner"]); $i ++){
		$miner = $zone["miner"][$i];
		$miner2 = $zone2["miner"][$i];
		$n = floor($i / $miner_per_table);
		$x = floor(($i % $miner_per_table) / $zone["layers"]);
		$y = ($i % $miner_per_table) % $zone["layers"];
        $ports = array();
        $mod_num = 0;
        foreach($miner["cgminer"] as $cgminer){
            $ports[] = $cgminer["port"];
            foreach($cgminer["mod"] as $mod) $mod_num += $mod;
        }
		if($miner2['alive'] == 'True')
		{
			$content = "<p class=\"tmap\">" . $miner2['modnum'];
			$content = $content . "<font color=\"white\">";
			switch($miner2['d_modnum'])
			{
			case 1:
				$content = $content . "&#x2B06&#x2B06";
				break;
			case -1:
				$content = $content . "&#x2B07&#x2B07";
				break;
			case 0:
				$content = $content . "  ";
				break;
			}
			$content = $content . "</font>";
			$content = $content . "</p><p class=\"tmap\">" . $miner2['hashrate'];
			$content = $content . "<font color=\"white\">";
			switch($miner2['d_hashrate'])
			{
			case 2:
				$content = $content . "&#x2B06&#x2B06";
				break;
			case -2:
				$content = $content . "&#x2B07&#x2B07";
				break;
			case 1:
				$content = $content . " &#x2B06";
				break;
			case -1:
				$content = $content . " &#x2B07";
				break;
			case 0:
				$content = $content . "  ";
				break;
			}
			$content = $content . "</font>";
			$content = $content . "</p><p class=\"tmap\">" . round($miner2['tempavg'],1) . "/" . $miner2['tempmax'] . "</p>";
		}
        elseif($mod_num > 0) $content = "<p class=\"tmap\"><font color=\"red\">N/A</font></p>";
        else $content = "";
		$zone_map[$n][$y][$x] = "<td title=\"" . $miner["ip"] . "\" class=\"tmap\" style=\"background:" . $miner2['color'] .
			"\" onclick=\"window.open('" . "cgminer.php?ip=" . $miner["ip"] . "&port=" . join(",",$ports) . "');\">" .
			$content 
			. "</td>";
	}	
	$farm_map[] = $zone_map;
	$z ++;
}
## Hashrate Graph
$timeshift = 8 * 3600;
$file = file_get_contents("bin/hashrate.log");
$lines = explode("\n",$file);
if (end($lines) == "") {
	    array_pop($lines);
}
$hashrates = array();
$series = array_fill(0, 4, array());
$now = time();
foreach($series as &$serie){
	$serie['pointStart'] = $now * 1000 - 3600 * 1000;
	$serie['pointInterval'] = 3600 * 1000;
	$serie['data'] = array();
}
$series[0]['color'] = "blue"; 
$series[1]['color'] = "cyan"; 
$series[2]['color'] = "green"; 
$series[3]['color'] = "red"; 
$series[0]['name'] = "Local Method 1"; 
$series[1]['name'] = "Local Method 2"; 
$series[2]['name'] = "Pool Worker"; 
$series[3]['name'] = "Pool Sum"; 
foreach($lines as $line) $hashrates[] = explode(";",$line);
foreach($hashrates as $hashrate){
	$unix = DateTime::createFromFormat('Y_m_d_H_i', $hashrate[0])->getTimestamp();
	$localtime = ($unix + $timeshift) * 1000;
	if($now - 24.5*3600 > $unix) continue;
	$series[0]['data'][] = array($localtime,$hashrate[1] * 1000000);
	$series[1]['data'][] = array($localtime,$hashrate[2] * 1000000);
	$series[2]['data'][] = array($localtime,$hashrate[3] * 1000000);
	$series[3]['data'][] = array($localtime,$hashrate[4] * 1000000);
}
?>

<html>
<link rel="stylesheet" href="css/bootstrap.min.css">
<link rel="stylesheet" href="css/style.css" />
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<script src="js/jquery.min.js"></script>
<script src="js/bootstrap.min.js"></script>
<script src="js/comm.js"></script>
<script src="js/highcharts.js"></script>
<script>
function refresh(){
	$.ajax({
		type:"POST",
		url:"refresh.php",
		data:{},
		dataType:"json",
		success:function(data){
			alert(data.msg);
		}
	});
}
</script>
<script>
$(function () { 
	$('#hashrate').highcharts({
		credits: {enabled: false},
		plotOptions: {line:{lineWidth:1,marker:{radius:2,symbol:"circle"}}},
		title: {text:'Hash Rate Graph'},
		yAxis: {title:{text:'Hash/s'}},
		xAxis: {
			title:{text:'Time (UTC+8)'},
			tickInterval: 2 * 3600 * 1000,	
            		type: 'datetime',
            		dateTimeLabelFormats: {
                		minute: '%H:%M'
            		}
        	},
		series: <?php echo json_encode($series); ?>
	});
});
</script>
<body>
	<div class="row">
		<!--Left Start-->
		<div class="col-md-6">
			<div class="jumbotron">
			<h2>Generated at <?php echo $status["time"] ?></h2>
			<!--<button onClick="refresh();">Refresh</button>-->
			</div>
			<div class="jumbotron">
<?php
$s = 1;
foreach($farm_map as $zone_map){
	for($n = 0; $n < count($zone_map); $n ++){
		echo "<table class=\"tmap\"><tbody>";
		for($y = 0; $y < count($zone_map[$n]);$y ++){
			echo "<tr><td class=\"yaxis\"><p class=\"axis\">";
			echo count($zone_map[$n])-$y . "</p></td>"; 
			for($x = 0; $x < count($zone_map[$n][$y]);$x ++) echo $zone_map[$n][$y][$x];
			echo "</tr>";
		}
		echo "<tr><td class=\"xaxiis\">  </td>";
		for($x = 0; $x < count($zone_map[$n][0]);$x ++){
			if($zone_map[$n][0][$x] === ' ') echo "<td class=\"xaxis\"> </td>";
			else{
				echo "<td class=\"xaxis\"><p class=\"axis\">" . $s . "</td>";
				$s ++;
			}
		}
		echo "</tr>";
		echo "</tbody></table>";
	}
}
?>
			</div>
			<div class="jumbotron">
				<div id="hashrate" style="width:100%; height: 720px !important;"></div>
			</div>
		</div>
		<!--Left End-->
		<!--Right Start-->
		<div class="col-md-6">
			<div class="jumbotron">
			<h3><strong>Active IP</strong>:     <?php echo $status["active_ip_num"]; ?></h2>
			<h3><strong>Alive Modules</strong>:     <?php echo $status["alive_mod_num"]; ?></h2>
				<h3>Error List:</h3>
					<table class="table table-bordered table-striped">
						<thead>
							<tr>
								<td><strong>IP</strong></td>
								<td><strong>Error</strong></td>
							</tr>
						</thead>
						<tbody>
<?php
if(count($status["err_miner_list"]) === 0) echo "<tr><td>None</td><td>None</td></tr>";
else{
	foreach($status["err_miner_list"] as $err_miner){
		$lines = explode(" ",$err_miner["id"]);
		switch(count($lines)){
		case 1:
			if(strpos($lines[0],":") == False){
				foreach($zones as $zone)
				foreach($zone["miner"] as $miner)
					if($miner["ip"] == $lines[0]){
						$ports = array();
						foreach($miner["cgminer"] as $cgminer) $ports[] = $cgminer["port"];
						$href = "cgminer.php?ip=" . $lines[0] . "&port=" . join(",",$ports);
						break;
					}
			}else{
				$liness = explode(":",$lines[0]); 
			       	$href = "cgminer.php?ip=" . $liness[0] . "&port=" . $liness[1];
			}
			break;
		case 2:
			$liness = explode(":",$lines[0]);
			$href = "cgminer.php?ip=" . $liness[0] . "&port=" . $liness[1] . "&hl=" . substr(explode("#",$lines[1])[1],0,1); 
			break;
		case 3:
			$liness = explode(":",$lines[0]);
			$href = "cgminer.php?ip=" . $liness[0] . "&port=" . $liness[1] . "&hl=" . explode(',',explode("#",$lines[1])[1])[0] . "-" . explode("#",$lines[2])[1]; 
			break;
		}
		echo "<tr><td><a href=\"" . $href . "\">" . $err_miner["id"] . "</a></td><td>";
		foreach($err_miner["error"] as $err) echo "<font color=\"" . $err["color"] . "\">" . $err["msg"] . "</font>";
		echo "</td></tr>";
	}
}
?>
						</tbody>
					</table>
			</div>
		</div>
		<!--Right end-->
	</div>
</body>
</html>

