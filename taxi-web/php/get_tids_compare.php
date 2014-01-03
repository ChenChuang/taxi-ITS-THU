<?php
	$fromtid = $_REQUEST['fromtid'];
	$totid = $_REQUEST['totid']; 
	$conn = pg_connect("dbname=beijing_taxi host=localhost user=postgres");
    $sql1 = "select tid from taxi_paths_compare where 
        (bn=0 or 
        st=0 or 
        iv=0 or 
        ut=0 or 
        uti=0) and 
        tid >= $1 
        and tid <= $2";
    $sql2 = "select tid from taxi_paths_uti where tid >= $1 and tid <= $2 and tid in (select tid from taxi_tracks_attr where length/rds_num >= 0 and length/rds_num <= 0.4 and tid <= 1000 and length > 5)";
    $sql3 = "select tid from taxi_paths_ut where tid in (18,28,69,73,84,96,97,451,456,464,476,477,479,481,483,501,505,548,550,658,662,691,724,727,735,768,784,891,940) and tid >= $1 and tid <= $2 order by tid";
    $result = pg_query_params($conn, $sql1, array($fromtid, $totid));
	if (!$result) {
    	echo ":(\n";
	} else {
        $tids = pg_fetch_all($result);
		echo json_encode($tids);
    }
    pg_close($conn);
?>

