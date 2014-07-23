<?php
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
		foreach($miner["cgminer"] as $cgminer) $ports[] = $cgminer["port"];
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
		else $content = "N/A";
		$zone_map[$n][$y][$x] = "<td class=\"tmap\" style=\"background:" . $miner2['color'] .
			"\" onclick=\"window.open('" . "cgminer.php?ip=" . $miner["ip"] . "&port=" . join(",",$ports) . "');\">" .
			$content 
			. "</td>";
	}	
	$farm_map[] = $zone_map;
	$z ++;
}
?>

<html>
<link rel="stylesheet" href="css/bootstrap.min.css">
<link rel="stylesheet" href="css/style.css" />
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<script src="js/jquery.min.js"></script>
<script src="js/bootstrap.min.js"></script>
<script src="js/comm.js"></script>
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
			if($zone_map[$n][$y][$x] === ' ') echo "<td class=\"xaxis\"> </td>";
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
				<div class="jumbotron">
					<a href="#" class="thumbnail">
						<img data-src="images/fox1.png" src="images/fox1.png" alt="...">
					</a>
				</div>
		</div>
		<!--Right end-->
	</div>
</body>
</html>

