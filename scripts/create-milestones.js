const { Octokit } = require("@octokit/rest");

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN,
});

async function createSprintMilestones() {
  const owner = "ApacheEcho";
  const repo = "RouteForceRouting";
  const sprintDuration = 14; // days
  
  for (let i = 1; i <= 4; i++) {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + (i - 1) * sprintDuration);
    
    const dueDate = new Date(startDate);
    dueDate.setDate(dueDate.getDate() + sprintDuration - 1);
    
    await octokit.issues.createMilestone({
      owner,
      repo,
      title: `Sprint ${i} - ${startDate.toLocaleDateString()}`,
      description: `Sprint ${i} goals and deliverables`,
      due_on: dueDate.toISOString(),
    });
  }
}

createSprintMilestones();