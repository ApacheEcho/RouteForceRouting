#!/usr/bin/env node

// Enhanced GitHub Project Setup Script
// Run with: node scripts/setup-project-fields.js

const customFields = [
  {
    name: "Story Points",
    type: "number",
    description: "Estimated effort (1, 2, 3, 5, 8, 13)"
  },
  {
    name: "Sprint",
    type: "single_select",
    options: ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4", "Backlog"]
  },
  {
    name: "Component",
    type: "single_select", 
    options: ["Backend", "Frontend", "API", "Database", "DevOps", "Documentation"]
  },
  {
    name: "Due Date",
    type: "date"
  },
  {
    name: "Blocked By",
    type: "text",
    description: "Issue numbers blocking this work"
  },
  {
    name: "Priority",
    type: "single_select",
    options: ["High", "Medium", "Low"]
  }
];

const automationRules = [
  {
    name: "Auto-add new issues",
    trigger: "Item added to project",
    action: "Set Status to 'Backlog'"
  },
  {
    name: "Move to In Progress",
    trigger: "Item labeled with 'in-progress'",
    action: "Set Status to 'In Progress'"
  },
  {
    name: "Move to Done",
    trigger: "Item closed",
    action: "Set Status to 'Done'"
  },
  {
    name: "High Priority Labeling",
    trigger: "Item title contains 'urgent' or 'critical'",
    action: "Set Priority to 'High'"
  }
];

console.log("🚀 GitHub Project Configuration");
console.log("==============================");
console.log("\n📋 Custom Fields to Add:");
customFields.forEach((field, index) => {
  console.log(`${index + 1}. ${field.name} (${field.type})`);
  if (field.description) console.log(`   Description: ${field.description}`);
  if (field.options) console.log(`   Options: ${field.options.join(', ')}`);
  console.log("");
});

console.log("\n⚡ Automation Rules to Configure:");
automationRules.forEach((rule, index) => {
  console.log(`${index + 1}. ${rule.name}`);
  console.log(`   When: ${rule.trigger}`);
  console.log(`   Then: ${rule.action}`);
  console.log("");
});

console.log("📝 Setup Instructions:");
console.log("1. Go to your GitHub repository");
console.log("2. Click on the 'Projects' tab");
console.log("3. Create a new project or select existing one");
console.log("4. Add the custom fields listed above via project settings");
console.log("5. Configure automation rules in project settings");
console.log("6. Update PROJECT_URL variable in repository settings if using automated workflows");

// If environment supports it, try to use GitHub CLI
if (process.env.GITHUB_TOKEN) {
  console.log("\n🔧 GitHub Token detected - automation setup possible");
  console.log("Run this script with --setup flag to attempt automated configuration");
}

module.exports = { customFields, automationRules };
