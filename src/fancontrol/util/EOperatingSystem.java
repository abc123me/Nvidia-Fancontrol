package fancontrol.util;

public enum EOperatingSystem {
	Windows, Linux, Mac, Solaris, FreeBSD, OtherUnixLike, Other;
	
	public static final EOperatingSystem BEST_OS = Linux;
	public static final EOperatingSystem CURRENT_OS = getOS();
	
	public static EOperatingSystem getOS() {
		String name = System.getProperty("os.name").toLowerCase().trim();
		if(name.contains("linux")) return Linux;
		if(name.contains("freebsd")) return FreeBSD;
		if(name.contains("sunos")) return Solaris;
		if(name.contains("win")) return Windows;
		if(name.contains("mac")) return Mac; 
		if(name.contains("nix")) return OtherUnixLike;
		return Other;
	}
}
