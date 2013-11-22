package com.its.android;

import java.io.BufferedReader;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import com.mapquest.android.maps.GeoPoint;

import android.annotation.SuppressLint;
import android.os.StrictMode;
import android.util.Log;


public class JSONParser {

	/**
	 * Pure URL for routing, without parameters appended.
	 */
    String route_url = "http://219.223.168.200/pgrouting-web/php/pgrouting.php";
    

    /**
     * Constructor of JSONParser.
     */
    public JSONParser() {}


    /**
     * Retrieve string in JSON format from given URL. 
     * @param url valid URL that returns string in JSON format.
     * @return valid JSONObject instance, or null if error occurred or parameters are invalid.
     */
    @SuppressLint("NewApi")
	private JSONObject getJSONFromUrl(String url) {
    	

    	//some codes to prevent error(forgotten) of HTTP connection. Maybe not a good idea.
    	StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
    	StrictMode.setThreadPolicy(policy);


    	InputStream inputstream = null;
    	JSONObject jsonobject = null;
    	String rawjson = "";

    
    	//try to connect to server with HTTP
        try {
		
            DefaultHttpClient httpclient = new DefaultHttpClient();            
            HttpGet httpget = new HttpGet(url);
            HttpResponse httpresponse = httpclient.execute(httpget);
            HttpEntity httpentity = httpresponse.getEntity();
            inputstream = httpentity.getContent();

        } catch (Exception e) {
		
            e.printStackTrace();

            return null;
        }
        

        //try to read string from stream
        try {
		
            BufferedReader reader = new BufferedReader(new InputStreamReader(inputstream, "iso-8859-1"), 8);
            StringBuilder stringbuilder = new StringBuilder();
            String line = null;
			
            while ((line = reader.readLine()) != null) {
            	stringbuilder.append(line + "\n");
            }

            inputstream.close();
            rawjson = stringbuilder.toString();

        } catch (Exception e) {

            Log.e("Buffer Error", "Error converting result " + e.toString());
            return null;
        }


        //try to parse raw string in JSON to JSONObject instance
        try {

        	jsonobject = new JSONObject(rawjson);

        } catch (JSONException e) {

            Log.e("JSON Parser", "Error parsing data " + rawjson);
            return null;
        }

        return jsonobject;

    }

    

    /**
     * Given start longitude/latitude and target longitude/latitude, request routing path from server. 
     * EPSG4326 is used in projection of longitude/latitude

     * @param start_lon longitude of start point in double
     * @param start_lat latitude of start point in double
     * @param target_lon longitude of target point in double
     * @param target_lat latitude of target point in double
     * @param route_method name of routing algorithm. 'SPD','SPA','SPS' are available.
	 
     * @return ArrayList<GeoPoint> representing the path, or null if error occurred or parameters are invalid.
     */

    public ArrayList<GeoPoint> getRoute(

    		double start_lon, 
    		double start_lat, 
    		double target_lon, 
    		double target_lat,
    		String route_method) {


    	//append parameters to URL of routing service.
    	String url = this.route_url + "?" + 
    			"startpoint=" + start_lon + "+" + start_lat + "&" +
    			"finalpoint=" + target_lon + "+" + target_lat + "&" +
    			"method=" + route_method;


    	//call getJSONFromUrl
		JSONObject jsonobject = this.getJSONFromUrl(url);

		ArrayList<GeoPoint> points = new ArrayList<GeoPoint>();


		//parse JSONObject instance to path
		try {
			//correct direction of every road segment
		    JSONArray features = jsonobject.getJSONArray("features");
		    JSONObject geo, s0_geo, s1_geo;
			JSONArray coords, s0_coords, s1_coords;
			JSONArray lon_lat, s0_start_ll, s0_end_ll, s1_start_ll, s1_end_ll, start_ll, end_ll;
			double last_lon=0, last_lat=0;


			//1st road segment
			s0_geo = features.getJSONObject(0).getJSONObject("geometry");
	    	s0_coords = s0_geo.getJSONArray("coordinates");
	    	s0_start_ll = s0_coords.getJSONArray(0);
	    	s0_end_ll = s0_coords.getJSONArray(s0_coords.length() - 1);
	    	
	    	//2nd road segment
	    	s1_geo = features.getJSONObject(1).getJSONObject("geometry");
	    	s1_coords = s1_geo.getJSONArray("coordinates");
	    	s1_start_ll = s1_coords.getJSONArray(0);
	    	s1_end_ll = s1_coords.getJSONArray(s1_coords.length() - 1);
	    	

	    	//compare 1st and 2nd segment to decide start point of the path
	    	if (s0_start_ll.equals(s1_start_ll) || s0_start_ll.equals(s1_end_ll)){
			
	    		for(int j = s0_coords.length() - 1; j >= 0; j--){
				
		    		lon_lat = s0_coords.getJSONArray(j);
		    		points.add(new GeoPoint((double)(lon_lat.getDouble(1)), (double)(lon_lat.getDouble(0))));
		    		//Log.d("DEBUG", points.get(points.size()-1).getLatitudeE6() + "," + points.get(points.size()-1).getLongitudeE6());
		    	}

	    		last_lon = s0_start_ll.getDouble(0);
	    		last_lat = s0_start_ll.getDouble(1);

	    	}else if (s0_end_ll.equals(s1_start_ll) || s0_end_ll.equals(s1_end_ll)){

	    		for(int j = 0; j < s0_coords.length(); j++){

		    		lon_lat = s0_coords.getJSONArray(j);
		    		points.add(new GeoPoint((double)(lon_lat.getDouble(1)), (double)(lon_lat.getDouble(0))));
		    		//Log.d("DEBUG", points.get(points.size()-1).getLatitudeE6() + "," + points.get(points.size()-1).getLongitudeE6());
		    	}

	    		last_lon = s0_end_ll.getDouble(0);
	    		last_lat = s0_end_ll.getDouble(1);

	    	}else {

	    		Log.e("data ERROR",s0_start_ll.toString() + s0_end_ll.toString() + s1_start_ll.toString() + s1_end_ll.toString());

	    		return null;				
	    	}

	    	//Log.d("DEBUG","------------");

	    	
	    	//add points to path in correct order
		    for(int i = 1; i < features.length(); i++){

		    	geo = features.getJSONObject(i).getJSONObject("geometry");
		    	coords = geo.getJSONArray("coordinates");
		    	start_ll = coords.getJSONArray(0);
		    	end_ll = coords.getJSONArray(coords.length() - 1);

		    	

		    	if (start_ll.getDouble(0) == last_lon && start_ll.getDouble(1) == last_lat){

		    		for(int j = 1; j < coords.length(); j++){

			    		lon_lat = coords.getJSONArray(j);
			    		points.add(new GeoPoint((double)(lon_lat.getDouble(1)), (double)(lon_lat.getDouble(0))));
			    		//Log.d("DEBUG", points.get(points.size()-1).getLatitudeE6() + "," + points.get(points.size()-1).getLongitudeE6());
			    	}

		    		last_lon = end_ll.getDouble(0);
		    		last_lat= end_ll.getDouble(1);

		    	}else if (end_ll.getDouble(0) == last_lon && end_ll.getDouble(1) == last_lat){

		    		for(int j = coords.length() - 2; j >= 0; j--){

			    		lon_lat = coords.getJSONArray(j);
			    		points.add(new GeoPoint((double)(lon_lat.getDouble(1)), (double)(lon_lat.getDouble(0))));
			    		//Log.d("DEBUG", points.get(points.size()-1).getLatitudeE6() + "," + points.get(points.size()-1).getLongitudeE6());
			    	}

		    		last_lon = start_ll.getDouble(0);
		    		last_lat= start_ll.getDouble(1);
					
		    	}else {

		    		Log.e("data ERROR", "(" + last_lon + "," + last_lat + ")" + start_ll.toString() + end_ll.toString());
		    		return null;
		    	}

		    	//Log.d("DEBUG","------------");
		    }

		} catch (Exception e) {

		    e.printStackTrace();
		    return null;
		}

		return points;
    }

}


