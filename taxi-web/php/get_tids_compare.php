<?php
	$fromtid = $_REQUEST['fromtid'];
	$totid = $_REQUEST['totid']; 
	$conn = pg_connect("dbname=beijing_taxi host=localhost user=postgres");
    $sql = "select tid from taxi_paths_compare where 
        (bn=0 or 
        st=0 or 
        iv=0 or 
        ut=0 or 
        uti=0) and 
        tid >= $1 
        and tid <= $2 and tid in (select tid from taxi_tracks_attr where length/rds_num > 0.0 and length/rds_num < 0.2 and tid < 1000)";
	$result = pg_query_params($conn, $sql, array($fromtid, $totid));
	if (!$result) {
    	echo ":(\n";
	} else {
        $tids = pg_fetch_all($result);
		echo json_encode($tids);
    }
    pg_close($conn);
?>

