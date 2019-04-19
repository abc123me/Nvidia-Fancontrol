package fancontrol.util;

public interface IDevice {
	public String getName();								//Returns the name of the device
	public boolean request();								//Requests access to the device, returns true if achieved
	public void release();									//Called when the device is no longer being used
	
	public interface IFanControl extends IDevice {
		public float getFanSpeed();							//Returns the fan speed as a percent between 0 and 1
		public boolean setFanSpeed(float to);				//Sets the fan speed to a value between 0 and 1, returns true on success
	}
	public interface ITempSensor extends IDevice {
		public float getTemperatureC(); 					//Returns the temperature in celcius
	}
	public interface IUtilizationSensor extends IDevice {
		public float getResourceTotal(); 					//Returns the amount of resource total
		public float getResourceUsed();						//Returns the amount of resource used up
		public float getResourceFree();						//Returns the amount of resource free for use
	}
}
