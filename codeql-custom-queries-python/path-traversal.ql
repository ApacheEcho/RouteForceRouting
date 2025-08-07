/**
 * Find potential path traversal vulnerabilities in routing system
 * @name Path traversal vulnerability
 * @kind problem
 * @problem.severity error
 * @id python/routing/path-traversal
 */

import python

from Call call, Expr pathArg
where 
  // File operations that could be vulnerable to path traversal
  (call.getFunc().toString() = "open" or
   call.getFunc().toString() = "os.path.join" or
   call.getFunc().(Attribute).getName() = "open" or
   call.getFunc().(Attribute).getName() = "read" or
   call.getFunc().(Attribute).getName() = "write" or
   call.getFunc().(Attribute).getName() = "remove" or
   call.getFunc().(Attribute).getName() = "unlink" or
   call.getFunc().(Attribute).getName() = "exists") and
  
  // Check if any argument contains path traversal patterns
  pathArg = call.getAnArg() and
  exists(string s | pathArg.toString() = s and 
    (s.regexpMatch(".*\\.\\.[\\/\\\\].*") or 
     s.regexpMatch(".*[\\/\\\\]\\.\\.[\\/\\\\].*") or
     s.indexOf("../") >= 0 or
     s.indexOf("..\\") >= 0))

select call, "Possible path traversal: file operation with directory traversal patterns detected"
