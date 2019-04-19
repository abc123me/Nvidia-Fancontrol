package fancontrol.util;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.Map;

public class Utility {
	public static final String DECIMAL_REGEXP = "^[0-9]*[.]?[0-9]+$";
	public static final String INTEGER_REGEXP = "^[0-9]+$";
	
	/**
	 * Removes all whitespace from a string, determined by Character.isWhitespace
	 * @param The string with whitespace
	 * @return The string, but without whitespace
	 */
	public static final String removeWhitespace(String in) {
		String out = "";
		for(int i = 0; i < in.length(); i++) {
			char c = in.charAt(i);
			if(!Character.isWhitespace(c))
				out += c;
		}
		return out;
	}
	/**
	 * Gets the hostname of the current system using various differnet methods
	 * First tries the HOSTNAME enviroment variable, then tries
	 * the COMPUTERNAME enviroment variable, then tries using the hostname
	 * of the localhost network device
	 * @return The system's hostname
	 * @throws RuntimeException If hostname cannot be found
	 */
	public static final String getHostname() {
		Map<String, String> env = System.getenv();
	    if (env.containsKey("HOSTNAME")) return env.get("HOSTNAME");
	    else if (env.containsKey("COMPUTERNAME")) return env.get("COMPUTERNAME");
	    try {
	    	String hostname = InetAddress.getLocalHost().getHostName();
	    	if(hostname != null) return hostname;
	    } catch(UnknownHostException uhe) {}
	    throw new RuntimeException("Unable to get hostname!");
	}
	/**
	 * Gets the X11 display from $DISPLAY
	 * @return System.getenv("DISPLAY").split("[.]")[0]
	 */
	public static final String getX11Display() {
		String dsp = System.getenv("DISPLAY");
		if(dsp == null) return null;
		return dsp.split("[.]")[0];
	}
}
