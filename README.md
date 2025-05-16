# TimeRep implementation for INFO9014
> Project for the Knowledge Representation & Reasoning class taught at ULiège by Prof. C. Debruyne.

## Repository Structure

This repository holds all the relevant files created throughout the milestones of the project.

## Non-trivial Demonstrator

A .zip file containing all the necessary components for the non-trivial demonstrator is available in the releases. The demonstrator allows you to:

- Test SHACL rules against uploaded data
- Verify that data uploads don't corrupt the existing knowledge graph

### Running the Demonstrator

Once you've downloaded and unzipped the file, follow these steps:

1. Make sure Docker and Docker Compose are installed
2. Run:
   ```bash
   docker compose build
   ```
3. Run: 
   ```bash
   docker compose up
   ```
4. Access the demonstrator at: [http://localhost:8000](http://localhost:8000)
