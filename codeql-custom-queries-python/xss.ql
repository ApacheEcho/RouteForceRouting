/**
 * Find potential XSS vulnerabilities in routing system
 * @name Cross-site scripting (XSS) vulnerability
 * @kind problem
 * @problem.severity error
 * @id python/routing/xss
 */

import python

from Call call, Expr userInput
where 
  // Template rendering and output functions that could be vulnerable to XSS
  (call.getFunc().toString() = "render_template" or
   call.getFunc().toString() = "render_template_string" or
   call.getFunc().toString() = "Markup" or
   call.getFunc().toString() = "make_response" or
   call.getFunc().(Attribute).getName() = "render_template" or
   call.getFunc().(Attribute).getName() = "render_template_string" or
   call.getFunc().(Attribute).getName() = "write" or
   call.getFunc().(Attribute).getName() = "format") and
  
  // Check for user input that might contain XSS patterns
  userInput = call.getAnArg() and
  exists(string s | userInput.toString() = s and 
    (s.indexOf("<script") >= 0 or
     s.indexOf("<iframe") >= 0 or
     s.indexOf("<object") >= 0 or
     s.indexOf("<embed") >= 0 or
     s.indexOf("javascript:") >= 0 or
     s.indexOf("onclick") >= 0 or
     s.indexOf("onload") >= 0 or
     s.indexOf("onerror") >= 0 or
     s.regexpMatch(".*<[^>]*on\\w+.*") or      // Event handlers
     s.regexpMatch(".*<[^>]*javascript:.*") or // JavaScript URLs
     s.regexpMatch(".*<[^>]*data:.*")))        // Data URLs

select call, "Possible XSS: output function with potentially unsafe HTML/JavaScript patterns detected"
