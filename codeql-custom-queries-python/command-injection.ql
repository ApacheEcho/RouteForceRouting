/**
 * Find potential command injection vulnerabilities in routing system
 * @name Command injection vulnerability
 * @kind problem
 * @problem.severity error
 * @id python/routing/command-injection
 */

import python

from Call call, Expr cmdArg
where 
  // System command execution functions
  (call.getFunc().toString() = "os.system" or
   call.getFunc().toString() = "os.popen" or
   call.getFunc().toString() = "os.execv" or
   call.getFunc().toString() = "os.execve" or
   call.getFunc().toString() = "subprocess.call" or
   call.getFunc().toString() = "subprocess.run" or
   call.getFunc().toString() = "subprocess.Popen" or
   call.getFunc().(Attribute).getName() = "system" or
   call.getFunc().(Attribute).getName() = "popen" or
   call.getFunc().(Attribute).getName() = "call" or
   call.getFunc().(Attribute).getName() = "run") and
  
  // Check if command contains potential injection patterns
  cmdArg = call.getAnArg() and
  exists(string s | cmdArg.toString() = s and 
    (s.indexOf("$") >= 0 or      // Variable expansion
     s.indexOf(";") >= 0 or      // Command chaining
     s.indexOf("&&") >= 0 or     // Conditional execution
     s.indexOf("||") >= 0 or     // OR execution
     s.indexOf("|") >= 0 or      // Piping
     s.indexOf("`") >= 0 or      // Command substitution
     s.indexOf("$(") >= 0 or     // Command substitution
     s.regexpMatch(".*[&><].*"))) // Redirection

select call, "Possible command injection: system command with potentially unsafe patterns detected"
