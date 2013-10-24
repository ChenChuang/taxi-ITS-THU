<?php
	$tid = $_REQUEST['tid'];
	$valid = $_REQUEST['valid'];
	$conn = pg_connect("dbname=beijing_taxi host=localhost user=postgres");
	$sql = "insert into taxi_paths select * from taxi_paths_BN where tid = $1";
	$result = pg_query_params($conn, $sql, array($tid));
	if ($result) {	
		$sql = "insert into taxi_paths_attr (tid,valid) values ($1,$2)";
		$result = pg_query_params($conn, $sql, array($tid, $valid));
	}
	if (!$result) {
    	echo ":(";
	} else {
        echo ":)";
    }
    pg_close($conn);
?>

