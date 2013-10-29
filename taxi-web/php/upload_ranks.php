<?php
    $tid = $_REQUEST['tid'];
    $bn = $_REQUEST['bn'];
    $st = $_REQUEST['st'];
    $iv = $_REQUEST['iv'];
    $ut = $_REQUEST['ut'];
    $uti = $_REQUEST['uti'];

	$conn = pg_connect("dbname=beijing_taxi host=localhost user=postgres");
	$sql = "update taxi_paths_compare set (bn, st, iv, ut, uti) = ($1,$2,$3,$4,$5) where tid = $6";
	$result = pg_query_params($conn, $sql, array($bn, $st, $iv, $ut, $uti, $tid));
	if (!$result) {
    	echo ":(";
	} else {
        echo ":)";
    }
    pg_close($conn);
?>

