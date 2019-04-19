package fancontrol.devices;

import java.awt.HeadlessException;
import java.io.IOException;
import java.util.ArrayList;

import fancontrol.util.*;
import fancontrol.util.IDevice.*;

public class NvidiaSMI{
	public static final String NVIDIA_SETTINGS_COMMAND = "nvidia-settings";
	public static final String NVIDIA_SMI_COMMAND = "nvidia-smi";
	public static final float LEGACY_VERSION = 349.16f;
	public static final int NO_GPU = -1;
	
	public static final boolean HAS_NV_SMI = CommandResult.doesCommandExist(NVIDIA_SMI_COMMAND);
	public static final boolean HAS_NV_SETTINGS = CommandResult.doesCommandExist(NVIDIA_SETTINGS_COMMAND);
	public static final boolean IS_RUNNING_LINUX = EOperatingSystem.CURRENT_OS == EOperatingSystem.Linux;
	public static final boolean IS_SUPPORTED = HAS_NV_SMI && HAS_NV_SETTINGS && IS_RUNNING_LINUX;
	
	public final int gpu;
	public final float DRIVER_VERSION;
	public final boolean IS_LEGACY_DRIVER;
	public final boolean HAS_MEMORY_TEMPERATURE, HAS_CORE_TEMPERATURE, HAS_FANSPEED;
	public final String X11_DISPLAY, HOSTNAME;
	public final ITempSensor memorySensor, coreSensor;
	public final IFanControl fanController;
	
	private static final String CORE_TEMPERATURE_QUERY = "temperature.gpu";
	private static final String MEMORY_TEMPERATURE_QUERY = "temperature.memory";
	private static final String FAN_SPEED_QUERY = "fan.speed";
	private static final String DRIVER_VERSION_QUERY = "driver_version";
	private static final String PRODUCT_NAME_QUERY = "name";
	private static final String GPU_COUNT_QUERY = "count";
	private static final String CORE_UTILIZATION_QUERY = "utilization.gpu";
	private static final String MEMORY_UTILIZATION_QUERY = "utilization.memory";
	
	private final NvidiaSMI smi = this;
	private final Thread shutdownHook = new Thread() {
		@Override public void run() { smi.setManualFanControl(false); }
	};
	
	private static final ArrayList<NvidiaSMI> gpus;
	static {
		if(!IS_SUPPORTED) gpus = null;
		else gpus = new ArrayList<NvidiaSMI>();
		int cnt = getGpuCount();
		for(int i = 0; i < cnt; i++)
			gpus.add(new NvidiaSMI(i));
	}
	public static final ArrayList<NvidiaSMI> getGPUs(){ return gpus; }
	
	public static void main(String[] args) throws Exception{
		NvidiaSMI smi = new NvidiaSMI();
		smi.printSystemStatistics();
		smi.setManualFanControl(true);
		smi.setFanSpeed(1);
		Thread.sleep(10000);
		smi.printSystemStatistics();
		smi.setManualFanControl(false);
		Thread.sleep(10000);
		smi.printSystemStatistics();
	}
	
	private NvidiaSMI() { this(0); }
	private NvidiaSMI(int gpu) {
		validateSystem();
		this.gpu = gpu;
		X11_DISPLAY = Utility.getX11Display();
		if(X11_DISPLAY == null) 
			throw new HeadlessException("You must have an X11 display for this to work!");
		HOSTNAME = Utility.getHostname();
		if(HOSTNAME == null) 
			throw new NullPointerException("Hostname is null?!");
	
		DRIVER_VERSION = queryGpuFloat(DRIVER_VERSION_QUERY, gpu);
		HAS_MEMORY_TEMPERATURE = queryGpuExists(MEMORY_TEMPERATURE_QUERY, gpu);
		HAS_CORE_TEMPERATURE = queryGpuExists(CORE_TEMPERATURE_QUERY, gpu);
		HAS_FANSPEED = queryGpuExists(FAN_SPEED_QUERY, gpu);
		
		IS_LEGACY_DRIVER = DRIVER_VERSION <= LEGACY_VERSION; 
		if(IS_LEGACY_DRIVER) System.err.println("WARNING: Legacy drivers (" + LEGACY_VERSION + " and below) are not officially supported!");
		
		if(HAS_MEMORY_TEMPERATURE) {
			memorySensor = new ITempSensor() {
				@Override public String getName() { return smi.getProductIdentifier() + " memory";}
				@Override public void release() {}
				@Override public boolean request() { return true; }
				@Override public float getTemperatureC() { return smi.getMemoryTemperatureC(); }
			};
		} else memorySensor = null;
		if(HAS_CORE_TEMPERATURE) {
			coreSensor = new ITempSensor() {
				@Override public String getName() { return smi.getProductIdentifier() + " core";}
				@Override public void release() {}
				@Override public boolean request() { return true; }
				@Override public float getTemperatureC() { return smi.getCoreTemperatureC(); }
			};
		} else coreSensor = null;
		if(HAS_FANSPEED) {
			fanController = new IFanControl() {
				@Override public String getName() { return getProductIdentifier() + " fan"; }
				@Override public void release() { smi.setManualFanControl(false); }
				@Override public boolean request() { return smi.setManualFanControl(true); }
				@Override public boolean setFanSpeed(float to) { return smi.setFanSpeed(to); }
				@Override public float getFanSpeed() { return smi.getFanSpeed() / 100.0f; }
				@Override public ITempSensor[] getReleventTempSensors() { return new ITempSensor[] { coreSensor, memorySensor }; }
			};
		} else fanController = null;
		Runtime.getRuntime().addShutdownHook(shutdownHook);
	}
	/*
	 * Utility functions
	 */
	public String getName() { return "Nvidia SMI"; }
	public float getCoreTemperatureC() { return queryGpuFloat(CORE_TEMPERATURE_QUERY, gpu); }
	public float getMemoryTemperatureC() { return queryGpuFloat(MEMORY_TEMPERATURE_QUERY, gpu); }
	public String getProductName() { return queryGpu(PRODUCT_NAME_QUERY, gpu).trim(); }
	public String getProductIdentifier() { return getProductName() + " (" + gpu + ")"; }
	public float getFanSpeed() { return queryGpuFloat(FAN_SPEED_QUERY, gpu, true); }
	public float getCoreUsage() { return queryGpuFloat(CORE_UTILIZATION_QUERY, gpu, true); }
	public float getMemoryUsage() { return queryGpuFloat(MEMORY_UTILIZATION_QUERY, gpu, true); }
	public boolean setFanSpeed(float to) {
		int toi = Math.round(100 * to); 
		if(toi > 100) toi = 100;
		if(toi < 0) toi = 0;
		return trySetNvidiaSetting("fan:0", "GPUTargetFanSpeed", String.valueOf(toi));
	}
	public boolean setManualFanControl(boolean enabled) { 
		String to = "0"; if(enabled) to = "1";
		return trySetNvidiaSetting("GPUFanControlState", to); 
	}
	public void printSystemStatistics() {
		System.out.println("--------------------------------");
		System.out.println("GPU: " + getProductIdentifier());
		System.out.println("Driver version: " + DRIVER_VERSION + (IS_LEGACY_DRIVER ? " (legacy)" : ""));
		System.out.println("Hostname: \"" + HOSTNAME + X11_DISPLAY + "\"");
		if(HAS_FANSPEED) System.out.println("Fan speed: " + getFanSpeed() + "%");
		if(HAS_MEMORY_TEMPERATURE) System.out.println("Memory temperature: " + getMemoryTemperatureC() + "C");
		if(HAS_CORE_TEMPERATURE) System.out.println("Core temperature: " + getCoreTemperatureC() + "C");
		System.out.println("Core usage: " + getCoreUsage() + "%");
		System.out.println("Memory usage: " + getMemoryUsage() + "%");
	}
	/*
	 * NVIDIA SETTINGS
	 */
	public final boolean trySetNvidiaSetting(String name, String value) throws NvidiaSettingsException { return trySetNvidiaSetting("gpu: " + gpu, name, value); }
	public final boolean trySetNvidiaSetting(String loc, String name, String value) throws NvidiaSettingsException {
		String attrArg = "[" + loc + "]/" + name + "=" + value;
		CommandResult res = null;
		try {
			res = CommandResult.execute(NVIDIA_SETTINGS_COMMAND, "-a", attrArg);
		} catch (IOException e) { e.printStackTrace(); throw new RuntimeException("IOException when executing command");
		} catch (InterruptedException e) { e.printStackTrace(); throw new RuntimeException("Thread interrupted during execution of command!"); }
		String expected = "Attribute\'" + name + "\'(" + HOSTNAME + X11_DISPLAY + "[" + loc + "])assignedvalue" + value + ".";
		String got = res.stdout.trim() + res.stderr.trim();
		got = Utility.removeWhitespace(got); expected = Utility.removeWhitespace(expected);
		if(expected.equals(got)) return true;
		else throw new NvidiaSettingsException(name, value, expected, got);
	}
	/*
	 * NVIDIA SMI
	 */
	public static final int getGpuCount() { return IS_SUPPORTED ? queryGpuInt(GPU_COUNT_QUERY, NO_GPU) : 0; }
	public static final String queryGpu(String attr, int gpu) throws NvidiaSMIQueryException {
		CommandResult res = null;
		try {
			if(gpu >= 0) res = CommandResult.execute(NVIDIA_SMI_COMMAND, "-i", String.valueOf(gpu), "--query-gpu=" + attr, "--format=csv,noheader");
			else res = CommandResult.execute(NVIDIA_SMI_COMMAND, "--query-gpu=" + attr, "--format=csv,noheader");
		} catch (IOException e) { e.printStackTrace(); throw new RuntimeException("IOException when executing command");
		} catch (InterruptedException e) { e.printStackTrace(); throw new RuntimeException("Thread interrupted during execution of command!"); }
		if(res == null) 
			throw new NvidiaSMIQueryException(attr, "command failed to execute", null);
		if(res.failed()) 
			throw new NvidiaSMIQueryException(attr, "command had a non-zero exit status", 
					"STDOUT: \"" + res.stdout + "\" \nSTDERR: \"" + res.stderr + "\"");
		return res.stdout;
	}
	public static final boolean queryGpuExists(String attr, int gpu) throws NvidiaSMIQueryException {
		String out = queryGpu(attr, gpu);
		if(out == null) throw new NvidiaSMIQueryException(attr);
		out = Utility.removeWhitespace(out.toLowerCase().trim());
		if(out.equals("n/a") || out.equals("n\\a")) return false;
		return true;
	}
	public static final int queryGpuInt(String attr, int gpu) throws NvidiaSMIQueryException { return queryGpuInt(attr, gpu, false); } 
	public static final float queryGpuFloat(String attr, int gpu) throws NvidiaSMIQueryException { return queryGpuFloat(attr, gpu, false); } 
	public static final float queryGpuFloat(String attr, int gpu, boolean allowPercent) throws NvidiaSMIQueryException {
		String out = queryGpu(attr, gpu);
		if(out == null) throw new NvidiaSMIQueryException(attr);
		out = out.trim();
		if(allowPercent && out.contains("%"))
			out = out.replace('%', ' ').trim();
		if(!out.matches(Utility.DECIMAL_REGEXP)) 
			throw new NvidiaSMIQueryException(attr, "output isn't a decimal", out);
		return Float.parseFloat(out);
	}
	public static final int queryGpuInt(String attr, int gpu, boolean allowPercent) throws NvidiaSMIQueryException {
		String out = queryGpu(attr, gpu);
		if(out == null) throw new NvidiaSMIQueryException(attr);
		out = out.trim();
		if(allowPercent && out.contains("%"))
			out = out.replace('%', ' ').trim();
		if(!out.matches(Utility.INTEGER_REGEXP)) 
			throw new NvidiaSMIQueryException(attr, "output isn't an integer", out);
		return Integer.parseInt(out);
	}
	/*
	 * Object cleanup
	 */
	@Override public void finalize() throws Throwable {
		Runtime.getRuntime().removeShutdownHook(shutdownHook);
		super.finalize();
	}
	/*
	 * Privates
	 */
	private static final void validateSystem() {
		if(EOperatingSystem.CURRENT_OS != EOperatingSystem.Linux)
			throw new RuntimeException("This implementation only works on linux!");
		if((!HAS_NV_SMI) || (!HAS_NV_SETTINGS))
			throw new RuntimeException("This cannot be used without nvidia proprietary drivers!");
	}
}
class NvidiaSMIQueryException extends RuntimeException{
	public final String query, result, reason;
	
	public NvidiaSMIQueryException(String query) {
		this(query, "output is null", null);
	}
	public NvidiaSMIQueryException(String query, String cause, String queryResult) {
		this.query = query;
		this.reason = cause.trim();
		if(queryResult != null) this.result = queryResult.trim();
		else this.result = null;
	}
	
	public String getMessage() {
		String msg = "nvidia-smi query failed because " + reason + System.lineSeparator();
		msg += "Query: \"" + query + "\"" + System.lineSeparator();
		if(result != null) msg += "Result: " + result;
		return msg;
	}
}
class NvidiaSettingsException extends RuntimeException{
	public final String attributeName, value, got, expected;

	public NvidiaSettingsException(String attributeName, String value, String expected, String got) {
		this.attributeName = attributeName;
		this.value = value;
		this.expected = expected;
		this.got = got;
	}
	
	public String getMessage() {
		String msg = "Failed setting " + attributeName + " to " + value + System.lineSeparator();
		if(expected != null && got != null)
			msg += "Expected: " + expected + System.lineSeparator() + "Got: " + got;
		return msg;
	}
}