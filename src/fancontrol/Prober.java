package fancontrol;

import java.util.ArrayList;

import fancontrol.devices.NvidiaSMI;
import fancontrol.devices.SysfsUtil;
import fancontrol.util.IDevice.*;

public class Prober {
	private static ArrayList<NvidiaSMI> gpus = NvidiaSMI.getGPUs();
	
	public static void main(String[] args) {
		System.out.println("Temperature sensors: ");
		for(ITempSensor its : probeTempSensors()) {
			if(its.request()) {
				System.out.println(its.getName() + ": " + its.getTemperatureC());
			} else {
				System.err.println("Failed to init temperature sensor");
			}
			its.release();
		}
		System.out.println("Fan controllers: ");
		for(IFanControl ifs : probeFanControllers()) {
			if(ifs.request()) {
				System.out.println(ifs.getName() + ": " + ifs.getFanSpeed());
				for(ITempSensor its : ifs.getReleventTempSensors())
					if(its != null) System.out.println("\tCools down: " + its.getName());
			} else {
				System.err.println("Failed to init fan controller");
			}
			ifs.release();
		}
	}
	
	public static ArrayList<ITempSensor> probeTempSensors(){
		ArrayList<ITempSensor> out = new ArrayList<ITempSensor>();
		for(NvidiaSMI gpu : gpus) {
			if(gpu == null) continue;
			if(gpu.coreSensor != null) out.add(gpu.coreSensor);
			if(gpu.memorySensor != null) out.add(gpu.memorySensor);
		}
		out.addAll(SysfsUtil.probeSysfs());
		return out;
	}
	public static ArrayList<IFanControl> probeFanControllers(){
		ArrayList<IFanControl> out = new ArrayList<IFanControl>();
		for(NvidiaSMI gpu : gpus) {
			if(gpu == null) continue;
			if(gpu.fanController != null) out.add(gpu.fanController);
		}
		return out;
	}
}
