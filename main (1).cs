class Program {

	private static void Run(string cmd, params string[] args) {
		var p = new System.Diagnostics.Process();

		p.StartInfo = new System.Diagnostics.ProcessStartInfo( cmd, string.Join(" ", args) ) 
			{
				UseShellExecute = false
			};

		p.Start();
		p.WaitForExit();
	}
	
	private static string FindAdb() {
		string[] paths = System.Environment.GetEnvironmentVariable("PATH").Split(';');
		foreach (string p in paths) {
			if (p.Contains("LucidEye"))
				continue;
			if (System.IO.File.Exists(System.IO.Path.Combine(p, "adb.exe")))
				return System.IO.Path.Combine(p, "adb.exe");
		}
		throw new System.Exception("ADB not found in PATH!");
	}

	public static void Main(string[] args) {
		string adb = FindAdb();
		string[] supportedCommands = new string[] { "devices", "shell" };
		
		if (args.Length > 0 && System.Array.IndexOf(supportedCommands, args[0]) != -1)
			Run("python", @"C:\LucidEye\BigMobileBrother.py", string.Format("\"{0}\"", adb));
		
		Run(adb, args);
	}
}