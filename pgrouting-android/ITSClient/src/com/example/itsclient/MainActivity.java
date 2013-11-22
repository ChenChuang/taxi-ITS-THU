package com.example.itsclient;

import java.util.ArrayList;

import org.osmdroid.tileprovider.tilesource.TileSourceFactory;
import org.osmdroid.util.GeoPoint;
import org.osmdroid.views.MapController;
import org.osmdroid.views.MapView;
import org.osmdroid.views.overlay.PathOverlay;

import android.os.Bundle;
import android.app.Activity;
import android.graphics.Color;
import android.graphics.Paint;
import android.view.Menu;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.RadioGroup;
import android.widget.RadioGroup.OnCheckedChangeListener;
import android.widget.Toast;

public class MainActivity extends Activity {

	Button btn_get;
	RadioGroup rgp;
	
	private MapController mMapController;
    private MapView mMapView;
    private PathOverlay mPathOverlay;
    private UserPointOverlay mUserPointOverlay;
    
    Paint pathpaint = null;
    
	double start_lon = 116.42991678032588;
	double start_lat = 39.961731751599174;
	double target_lon = 116.30288736138505;
	double target_lat = 39.86377070080956;
	
	String route_method = "SPD";
	
	JSONParser mJSONParser;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
		this.btn_get = (Button)findViewById(R.id.btn_get);
		this.rgp = (RadioGroup)findViewById(R.id.rgp);
		
		this.btn_get.setOnClickListener(new OnClickListener(){

			@Override
			public void onClick(View arg0) {
				// TODO Auto-generated method stub
				try {
					MainActivity.this.plotRoute( MainActivity.this.getRoute() );
				} catch (Exception e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
					Toast.makeText(getApplicationContext(), "ERROR: check your startpoint,targetpoint or server", Toast.LENGTH_SHORT).show();
				}
				MainActivity.this.mMapView.invalidate();
			}
			
		});
		
		this.rgp.setOnCheckedChangeListener(new OnCheckedChangeListener(){

			@Override
			public void onCheckedChanged(RadioGroup arg0, int arg1) {
				// TODO Auto-generated method stub
				MainActivity.this.mUserPointOverlay.setIsSelectingStartPoint(arg1 == R.id.rbt_sets);
			}
			
		});
		
		this.mMapView = (MapView) findViewById(R.id.mapview);
		this.mMapView.setTileSource(TileSourceFactory.MAPNIK);
		this.mMapView.setBuiltInZoomControls(true);
		this.mMapView.setMultiTouchControls(true);
		this.mMapController = this.mMapView.getController();
		this.mMapController.setZoom(10);
		this.mMapController.setCenter(new GeoPoint(39967600,116413062));
		
		this.mPathOverlay = new PathOverlay(Color.RED, this);
		this.mMapView.getOverlays().add(this.mPathOverlay);
		this.pathpaint = this.mPathOverlay.getPaint();
		this.pathpaint.setStrokeWidth(5);
		this.pathpaint.setColor(Color.RED);
		this.mPathOverlay.setPaint(this.pathpaint);
		
		this.mUserPointOverlay = new UserPointOverlay(this);
		this.mMapView.getOverlays().add(this.mUserPointOverlay);
		
		this.mJSONParser = new JSONParser();
	}
	

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.main, menu);
		return true;
	}
	
	private ArrayList<GeoPoint> getRoute() throws Exception{
		start_lon = this.mUserPointOverlay.getStartPoint().getLongitudeE6()/1000000f;
		start_lat = this.mUserPointOverlay.getStartPoint().getLatitudeE6()/1000000f;
		target_lon = this.mUserPointOverlay.getTargetPoint().getLongitudeE6()/1000000f;
		target_lat = this.mUserPointOverlay.getTargetPoint().getLatitudeE6()/1000000f;
		
		ArrayList<GeoPoint> points = this.mJSONParser.getRoute(start_lon, start_lat, target_lon, target_lat, route_method);
		if(points != null){
			for(int i=0; i < points.size(); i++){
				//Log.d("DEBUG", points.get(i).getLongitudeE6() + "," + points.get(i).getLatitudeE6());
			}
		}else{
			throw new Exception();
		}
		return points;
	}
	
	private boolean plotRoute(ArrayList<GeoPoint> points){
		this.mPathOverlay.clearPath();
		this.mPathOverlay.addPoint(points.get(0));
		this.mPathOverlay.addPoint(points.get(1));
		for(int i=2; i < points.size() - 1; i++){			
			this.mPathOverlay.addPoint(points.get(i));
			//Log.d("DEBUG", points.get(i).getLongitudeE6() + "," + points.get(i).getLatitudeE6());
		}
		this.mPathOverlay.addPoint(points.get(points.size() - 1));
		//Log.d("DEBUG", "points number = " + this.mPathOverlay.getNumberOfPoints());
		return true;
	}

}
