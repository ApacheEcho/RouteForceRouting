/**
 * Find potential SQL injection vulnerabilities in routing system
 * @name SQL injection vulnerability
 * @kind problem
 * @problem.severity error
 * @id python/routing/sql-injection
 */

import python

from Call call, Expr query
where call.getFunc().toString() = "execute" and
      call.getArg(0) = query and
      exists(string s | query.toString() = s and s.matches("%%" + "%" + "%%"))
select call, "Possible SQL injection: dynamic query construction detected"