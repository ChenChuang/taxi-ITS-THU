<?php
	$fromtid = $_REQUEST['fromtid'];
	$totid = $_REQUEST['totid']; 
	$conn = pg_connect("dbname=beijing_taxi host=localhost user=postgres");
	$sql = "select tid from taxi_paths_BN where tid not in (select tid from taxi_paths) and tid >= $1 and tid <= $2";
	$result = pg_query_params($conn, $sql, array($fromtid, $totid));
	if (!$result) {
    	echo ":(\n";
	} else {
        $tids = pg_fetch_all($result);
		echo json_encode($tids);
    }
    pg_close($conn);
?>

