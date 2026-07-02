export interface DocNode {
  title: string;
  slug: string;
  content: string;
  category: string;
}

export const docs: DocNode[] = [
  {
    title: "Installation Guide",
    slug: "installation",
    category: "Getting Started",
    content: `
# Installation Guide

Get up and running with Aetheris on your environment.

## Method 1: Local Installation

Aetheris requires Python 3.10+ and Node.js 18+.

\`\`\`bash
# Clone the repository
git clone https://github.com/aetheris-dev/aetheris.git
cd aetheris

# Install editable python package
pip install -e .
\`\`\`

## Method 2: Docker Deployment

Deploy the entire sandboxed execution environment inside Docker.

\`\`\`bash
# Run using docker-compose
docker-compose up -d --build
\`\`\`

## Configuration Parameters

Define your environment tokens inside a \`.env\` file in the root workspace folder:

\`\`\`env
AETHERIS_TOKEN=secure-aetheris-token-2026
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/aetheris
\`\`\`
`
  },
  {
    title: "Quick Start",
    slug: "quickstart",
    category: "Getting Started",
    content: `
# Quick Start Guide

Start building your first system with Aetheris in minutes.

## Step 1: Initialize Project

Initialize a new Aetheris configuration folder inside your workspace:

\`\`\`bash
aetheris init my-ecom-platform
\`\`\`

## Step 2: Set Objective Goals

Run the autonomous engineering loop by providing a goal string:

\`\`\`bash
aetheris --goal "Build an API middleware with JWT validation"
\`\`\`

## Step 3: Verify Output

The workspace discovery and planners will build structural tasks, execute the code editor, and run verification audits automatically.
`
  },
  {
    title: "Architecture Handbook",
    slug: "architecture",
    category: "Guides",
    content: `
# Architecture Handbook

Aetheris organizes software engineering tasks according to a strict hierarchical structure of Specifications and RFC guidelines.

## Conceptual Core Layers

1. **Intelligence Layer (RFC-001 - RFC-005)**: Walk files, understand goals, generate architectures, and select skills.
2. **Execution Layer (RFC-006 - RFC-008)**: Code editing editors, scheduled tasks, and recovery systems.
3. **Runtime Layer (RFC-000)**: Sandboxed process command runners.
4. **Learning Layer (RFC-009)**: Memory caching ledger of latency and quality.
`
  },
  {
    title: "CLI Reference",
    slug: "cli-reference",
    category: "Reference",
    content: `
# CLI Command Reference

Exposes options for control loops inside the Aetheris runtime.

## Core Commands

### aetheris --goal <string>
Executes the full pipeline loops (WDE, URUE, PDE, APE, ACGE, SRE, and DoD audits).

### aetheris init <name>
Bootstraps folders and files for a new project.

### aetheris status
Queries execution states from the EKB.
`
  }
];
