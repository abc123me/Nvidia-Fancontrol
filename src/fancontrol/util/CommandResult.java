package fancontrol.util;

import java.io.*;

public class CommandResult{
	public final String stderr, stdout;
	public final int exitCode;
	
	public CommandResult(int exitCode, String stdout, String stderr) {
		this.exitCode = exitCode;
		this.stdout = stdout;
		this.stderr = stderr;
	}
	
	public boolean failed() { return exitCode != 0; }
	
	public static final boolean doesCommandExist(String cmd) {
		if(cmd == null) return false;
		String[] path = System.getenv("PATH").split(":");
		for(String s : path) {
			if(s == null) continue;
			File fs = new File(s);
			if(fs == null) continue;
			if(fs.isDirectory()) {
				for(File fd : fs.listFiles())
					if(cmd.equals(fd.getName()))
						return true;
			} else if(cmd.equals(fs.getName())) return true;	
		}
		return false;
	}
	public static final CommandResult execute(String... cmd) throws IOException, InterruptedException { return execute(4096, cmd); }
	public static final CommandResult execute(int buflen, String... cmd) throws IOException, InterruptedException {
		ProcessBuilder pb = new ProcessBuilder(cmd);
		Process p = pb.start();
		int exit = p.waitFor();
		InputStream out = p.getInputStream();
		String stdout = readStreamToString(out, buflen);
		out.close();
		InputStream err = p.getErrorStream();
		String stderr = readStreamToString(err, buflen);
		err.close();
		return new CommandResult(exit, stdout, stderr);
	}
	private static final String readStreamToString(InputStream is, int maxLength) throws IOException {
		String out = "";
		int pos = 0;
		while(is.available() > 0) {
			if(pos++ >= maxLength) 
				throw new RuntimeException("Maximum length reached when reading from process!");
			out += (char) is.read();
		}
		return out;
	}
}