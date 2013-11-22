package com.example.itsclient;

import org.osmdroid.util.GeoPoint;
import org.osmdroid.views.MapView;
import org.osmdroid.views.MapView.Projection;
import org.osmdroid.views.overlay.Overlay;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Point;
import android.view.MotionEvent;

public class UserPointOverlay extends Overlay {

	protected Context mContext = null;
	private GeoPoint startpoint = null;
	private GeoPoint targetpoint = null;
	
	private Paint startpaint = new Paint(Paint.ANTI_ALIAS_FLAG);
	private Paint targetpaint = new Paint(Paint.ANTI_ALIAS_FLAG);
	
	private boolean isSelectingStartPoint = true;
	
	public UserPointOverlay(Context ctx) {
		super(ctx);
		// TODO Auto-generated constructor stub
		this.mContext = ctx;
		this.startpaint.setColor(Color.RED);
		this.targetpaint.setColor(Color.GREEN);
	}

	@Override
	protected void draw(Canvas canvas, MapView mapview, boolean arg2) {
		// TODO Auto-generated method stub
		
		Point p = new Point();
		if(this.startpoint != null){
			mapview.getProjection().toPixels(this.startpoint, p);
			canvas.drawCircle(p.x, p.y, 10, this.startpaint);
		}
		if(this.targetpoint != null){
			mapview.getProjection().toPixels(this.targetpoint, p);
			canvas.drawCircle(p.x, p.y, 10, this.targetpaint);
		}
		
	}

	@Override
	public boolean onLongPress(MotionEvent e, MapView mapView) {
		// TODO Auto-generated method stub
		Projection proj = mapView.getProjection();
        GeoPoint point = (GeoPoint) proj.fromPixels((int)e.getX(), (int)e.getY());
        if(this.isSelectingStartPoint){
        	this.startpoint = (GeoPoint) point;
        }else{
        	this.targetpoint = (GeoPoint) point;
        }
        mapView.invalidate();
		return super.onLongPress(e, mapView);
	}
	
	public void setIsSelectingStartPoint(boolean b){
		this.isSelectingStartPoint = b;
	}
	
	public GeoPoint getStartPoint(){
		return this.startpoint;
	}

	public GeoPoint getTargetPoint(){
		return this.targetpoint;
	}
}
