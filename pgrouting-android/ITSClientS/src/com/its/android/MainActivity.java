package com.its.android;

import java.util.ArrayList;

import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.drawable.Drawable;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Toast;

import com.mapquest.android.maps.DefaultItemizedOverlay;
import com.mapquest.android.maps.GeoPoint;
import com.mapquest.android.maps.ItemizedOverlay;
import com.mapquest.android.maps.LineOverlay;
import com.mapquest.android.maps.MapView;
import com.mapquest.android.maps.Overlay;
import com.mapquest.android.maps.OverlayItem;


public class MainActivity extends NavigationInten {
	
	ArrayList<GeoPoint> points = new ArrayList<GeoPoint>();
	ArrayList<GeoPoint> routeData = new ArrayList<GeoPoint>();
	
	JSONParser parser = new JSONParser();
	
	/**
	 * Initialize the map.
	 */
    @Override
    protected void init() {
        setupMapView(new GeoPoint(39.967600f,116.413062f), 10);
        
        TouchOverlay overlay = new TouchOverlay();
        map.getOverlays().add(overlay);
    }
    
    
    /**
	 * Construct a simple line overlay to display on the map and add a OverlayTapListener
	 * to respond to tap events.
	 * 
	 */
    private void showLineOverlayWithPoints(ArrayList<GeoPoint> routeData) {
        Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
            paint.setColor(Color.RED);
            paint.setAlpha(100);
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeJoin(Paint.Join.ROUND);
            paint.setStrokeCap(Paint.Cap.ROUND);
            paint.setStrokeWidth(10);
    		
            LineOverlay line = new LineOverlay(paint);
            line.setData(routeData);
            line.setShowPoints(true, null);
            line.setKey("Line #2");

    		line.setTouchEventListener(new LineOverlay.OverlayTouchEventListener() {			
    			@Override
    			public void onTouch(MotionEvent evt, MapView mapView) {
    				Toast.makeText(getApplicationContext(), "Line Touch!", Toast.LENGTH_SHORT).show();				
    			}
    		});
            this.map.getOverlays().add(line);
            this.map.invalidate();
            
    }
    	

    /**
     * Launch navigation to various locations based on clicking on the map.
     *
     */
    private class TouchOverlay extends Overlay { 
    	
    	public boolean onTap(GeoPoint p, final MapView mapView) {
    		
    		Drawable icon = getResources().getDrawable(R.drawable.location_marker);
 	        final DefaultItemizedOverlay poiOverlay = new DefaultItemizedOverlay(icon);
    		
    		Toast.makeText(getApplicationContext(), p.getLatitude() + "," + p.getLongitude(), Toast.LENGTH_LONG).show();
    	        // Limiting the number of markers in the map
    		if(points.size()<2) {
				points.add(p);
    	        
				// set GeoPoints and title/snippet to be used in the annotation view 
				poiOverlay.addItem(new OverlayItem(p, "", ""));
					
				// Send parameters to the server when two markers are displayed
				if (points.size() == 2) {
					routeData = parser.getRoute( points.get(0).getLongitude(), 
												 points.get(0).getLatitude(), 
    	        								 points.get(1).getLongitude(),
    	        								 points.get(1).getLatitude(),
    	        								 "SPS" );
    	        	
					if (routeData != null)
						showLineOverlayWithPoints(routeData);
					else 
						Log.e("ERROR","Route data error");
 	            
				} else exit(0);
    	             
				// add a tap listener
    	    	poiOverlay.setTapListener(new ItemizedOverlay.OverlayTapListener() {
    				@Override
    				public void onTap(GeoPoint pt, MapView mapView) {
    					// when tapped, deleted
    					poiOverlay.destroy();
    					points.clear();
    				}
    			});
    	    	
				// Listener : Clear the map when clicking on the button
    	    	resetButton.setOnClickListener(new View.OnClickListener() {	
    	 			@Override
    	 			public void onClick(View v) {
    	 			
    	 				// Clear overlays and points
    	 				map.getOverlays().clear();
    					points.clear();
   
    					//Realease the map
    					init();
    	 			}
    	 		});
    	        
    	        map.getOverlays().add(poiOverlay);
    	        map.invalidate();
    	        return true;
    		}
			
    		else exit(0);	
    		
    		return false;
    	}

		private void exit(int i) {
			// TODO Auto-generated method stub
		}
    }
}










