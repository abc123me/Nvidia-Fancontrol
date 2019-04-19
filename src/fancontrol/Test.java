package fancontrol;

import fancontrol.devices.SysfsUtil;
import fancontrol.util.IDevice.*;

public class Test {

	public static void main(String[] args) {
		for(ITempSensor its : SysfsUtil.probeSysfs()) {
			if(its.request()) {
				System.out.println(its.getName() + ": " + its.getTemperatureC());
			} else {
				System.err.println("Failed to init temperature sensor");
			}
			its.release();
		}
	}

}
