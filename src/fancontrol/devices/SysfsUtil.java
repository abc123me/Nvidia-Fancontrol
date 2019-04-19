package fancontrol.devices;

import java.util.*;
import java.io.*;

import fancontrol.util.IDevice.*;

public class SysfsUtil {
	public static final String SYSFS_TEMPERATE_SENSE_PATH = "/sys/class/thermal/";
	
	public static final ITempSensor openSysfsTempSensor(int id) {
		final String path = SYSFS_TEMPERATE_SENSE_PATH + "/thermal_zone" + id + "/temp";
		return new ITempSensor() {
			File fp = new File(path);
			FileInputStream fis;
			@Override public void release() {
				try{ fis.close(); } catch(IOException ioe) {}
			}
			@Override public float getTemperatureC() {
				byte[] buf = new byte[8];
				try{ fis.read(buf); } catch(IOException ioe) { return Float.NaN; }
				String s = "";
				for(int i = 0; i < buf.length; i++)
					if((buf[i] >= '0' && buf[i] <= '9') || buf[i] == '.') s += (char) buf[i]; else break;
				return Float.parseFloat(s) / 1000;
			}
			@Override public boolean request() {
				try{
					fis = new FileInputStream(fp); 
				} catch(IOException ioe) {
					return false;
				}
				return true; 
			}
			@Override public String getName() {
				return "Thermal zone " + id;
			}
		};
	}
	public static final ArrayList<ITempSensor> probeSysfs(){
		ArrayList<ITempSensor> out = new ArrayList<ITempSensor>();
		File sysfsDir = new File(SYSFS_TEMPERATE_SENSE_PATH);
		if(!sysfsDir.isDirectory())
			throw new RuntimeException(SYSFS_TEMPERATE_SENSE_PATH + " is not a directory?!");
		File[] subDirs = sysfsDir.listFiles();
		for(File sd : subDirs) {
			String s = sd.getName();
			if(s.matches("^(thermal_zone)([0-9]+)$"))
				out.add(openSysfsTempSensor(Integer.parseInt(s.substring(12))));
		}
		return out;
	}
}
