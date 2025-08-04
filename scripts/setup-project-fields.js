// This script adds custom fields to your GitHub Project
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
    options: ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4"]
  },
  {
    name: "Component",
    type: "single_select", 
    options: ["Backend", "Frontend", "API", "Database", "DevOps"]
  },
  {
    name: "Due Date",
    type: "date"
  },
  {
    name: "Blocked By",
    type: "text",
    description: "Issue numbers blocking this work"
  }
];

console.log("Add these custom fields to your project via GitHub UI");
customFields.forEach(field => console.log(field));
