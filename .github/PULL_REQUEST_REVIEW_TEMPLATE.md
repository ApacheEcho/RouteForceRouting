# 👨‍💻 Code Review Checklist

## 🎯 **Review Focus Areas**

### **Code Quality**
- [ ] Code follows project coding standards and conventions
- [ ] Functions and classes are appropriately sized and focused
- [ ] Variable and function names are clear and descriptive
- [ ] Code is DRY (Don't Repeat Yourself) and follows SOLID principles
- [ ] Complex logic is well-commented and documented

### **Functionality**
- [ ] Changes accomplish the stated goals
- [ ] Edge cases are properly handled
- [ ] Error handling is appropriate and informative
- [ ] User experience is intuitive and efficient
- [ ] Performance implications are considered

### **Security**
- [ ] No sensitive information is exposed or hardcoded
- [ ] Input validation is properly implemented
- [ ] Authentication and authorization are correctly handled
- [ ] SQL injection and XSS vulnerabilities are prevented
- [ ] Security best practices are followed

### **Testing**
- [ ] Adequate test coverage for new functionality
- [ ] Tests are meaningful and test actual behavior
- [ ] All tests pass in CI/CD pipeline
- [ ] Manual testing has been performed where appropriate
- [ ] Regression tests prevent future issues

### **Architecture & Design**
- [ ] Changes align with overall system architecture
- [ ] Dependencies are justified and minimal
- [ ] Database schema changes are backward compatible
- [ ] API changes maintain backward compatibility
- [ ] Design patterns are used appropriately

### **Documentation**
- [ ] Code changes are documented in relevant areas
- [ ] README.md is updated if needed
- [ ] API documentation reflects changes
- [ ] Inline documentation explains complex logic
- [ ] Breaking changes are clearly documented

### **RouteForce Routing Specific**
- [ ] Route optimization logic is efficient and accurate
- [ ] Geographic data handling is correct
- [ ] Map integrations work properly
- [ ] Performance meets routing requirements
- [ ] Algorithm choices are justified

---

## 📝 **Review Comments Template**

### **Approval Comments:**
```
✅ **LGTM!** Great work on [specific improvement]. 

**Highlights:**
- [What was done particularly well]
- [Positive impact on codebase]

**Minor suggestions:**
- [Any optional improvements]
```

### **Request Changes Comments:**
```
⚠️ **Changes Requested**

**Must Fix:**
- [Critical issues that block merge]

**Should Fix:**
- [Important improvements needed]

**Consider:**
- [Optional suggestions for improvement]
```

### **Question Comments:**
```
❓ **Question about [specific area]**

Could you clarify [specific question]? I want to make sure I understand [the reasoning/approach/implementation].
```

---

## 🔄 **Post-Review Actions**

After reviewing:
- [ ] Add appropriate labels to the PR
- [ ] Request additional reviewers if needed
- [ ] Verify CI/CD checks are passing
- [ ] Confirm PR is linked to relevant issues
- [ ] Check that milestone assignment is correct
