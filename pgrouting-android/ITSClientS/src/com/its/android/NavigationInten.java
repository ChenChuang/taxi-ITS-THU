package com.its.android;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import com.mapquest.android.maps.GeoPoint;
import com.mapquest.android.maps.MapActivity;
import com.mapquest.android.maps.MapView;
import com.mapquest.android.maps.MyLocationOverlay;

/**
 * Base class
 *
 */
public class NavigationInten extends MapActivity {
    
	protected MapView map; 
    protected MyLocationOverlay myLocationOverlay;
	protected Button followMeButton;
	protected Button resetButton;
	
	/** 
	 * Called when the activity is first created.  
	 */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(getLayoutId());
        
        followMeButton = (Button)findViewById(R.id.followMeButton);
        resetButton    = (Button)findViewById(R.id.reset);
        
        followMeButton.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View v) {
				//myLocationOverlay.setFollowing(true);
				setupMyLocation();
			}
		});
		
       init();
    }
    
    /**
     * Initialize the view.
     */
    protected void init() {
        setupMapView(new GeoPoint(39.80f, 116.5f), 12);
    }
    
    /**
	 * Set up the user's current location
	 *
	 */
    protected void setupMyLocation() {
		this.myLocationOverlay = new MyLocationOverlay(this, map);
		
		myLocationOverlay.enableMyLocation();
		myLocationOverlay.runOnFirstFix(new Runnable() {
		
			@Override
			public void run() {
				GeoPoint currentLocation = myLocationOverlay.getMyLocation(); 
				map.getController().animateTo(currentLocation);
				map.getController().setZoom(13);
				map.getOverlays().add(myLocationOverlay);
				myLocationOverlay.setFollowing(true);
			}
		});
	}

    /**
     * Set up a basic MapQuest map with zoom controls
     */
	protected void setupMapView(GeoPoint pt, int zoom) {
		this.map = (MapView) findViewById(R.id.map);

		// set the zoom level
		map.getController().setZoom(zoom);
		
		// set the center point
		map.getController().setCenter(pt);
		
		// enable the zoom controls
		map.setBuiltInZoomControls(true);
		
	}

	/**
	 * Get the id of the layout file.
	 * @return
	 */
	protected int getLayoutId() {
	    return R.layout.activity_main;
	}

	@Override
	protected boolean isRouteDisplayed() {
		return false;
	}

	
}