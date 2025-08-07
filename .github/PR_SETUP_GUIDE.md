# 🔧 GitHub PR Configuration Guide

## **Repository Settings to Configure**

### **1. Branch Protection Rules** 
Go to Settings → Branches → Add rule for `main`:

**Required Status Checks:**
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- Select: CodeQL, Security Check, Tests, Linting

**Required Reviews:**
- ✅ Require pull request reviews before merging
- Required approving reviews: **1**
- ✅ Dismiss stale PR approvals when new commits are pushed
- ✅ Require review from code owners
- ✅ Restrict pushes that create new files

**Other Restrictions:**
- ✅ Restrict pushes to matching branches  
- ✅ Allow force pushes: **Everyone**
- ✅ Allow deletions: **Disabled**

### **2. General Repository Settings**
Go to Settings → General:

**Pull Requests:**
- ✅ Allow merge commits
- ✅ Allow squash merging (default)
- ✅ Allow rebase merging
- ✅ Always suggest updating pull request branches
- ✅ Allow auto-merge
- ✅ Automatically delete head branches

**Merge Button:**
- Default to: **Squash and merge**
- ✅ Use pull request title for squash merge commits

### **3. Code Security and Analysis**
Go to Settings → Code security and analysis:

**Dependency Management:**
- ✅ Dependabot alerts
- ✅ Dependabot security updates  
- ✅ Dependabot version updates

**Code Scanning:**
- ✅ CodeQL analysis
- ✅ Push protection (if available)

### **4. Webhooks & Integrations**
Configure any external PR tools:
- Slack notifications
- Linear integration
- Code coverage tools
- CI/CD pipeline integrations

---

## **PR Workflow Summary**

### **For Contributors:**
1. Create feature branch from `main`
2. Make changes and commit with clear messages
3. Fill out PR template completely
4. Link PR to relevant issues
5. Ensure all CI checks pass
6. Request review from maintainers
7. Address review feedback promptly
8. Maintainer will squash and merge when approved

### **For Maintainers:**
1. Use review template for consistent feedback
2. Check all automated validations pass
3. Verify security and performance implications
4. Ensure documentation is updated
5. Approve and squash merge
6. Monitor post-merge CI/CD

---

## **Auto-Generated PR Features**

✅ **Automated Labeling** - PRs get labeled by file changes
✅ **Size Labeling** - PRs get size labels (XS, S, M, L, XL)
✅ **Issue Linking** - Auto-link issues mentioned in PR
✅ **Security Scanning** - Automatic security checks
✅ **Welcome Messages** - First-time contributors get welcomed
✅ **Requirement Validation** - Check PR template completion
