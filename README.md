# TimeRep implementation for INFO9014
> Project for the Knowledge Representation & Reasoning class taught at ULiège by Prof. C. Debruyne.

## Repository Structure

This repository holds all the relevant files created throughout the milestones of the project.

## Non-trivial Demonstrator

The non-trivial demonstrator is available as a single file `timerep-demonstrator.zip` at:
https://github.com/giooms/INFO9014/releases/tag/v1.0

The demonstrator allows you to:

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

Then, the following actions are possible: 

#### Basic RDF Validation Workflow

1. **Upload RDF data for validation:**

   - Click the "Select RDF File" button to choose a Turtle (.ttl), RDF/XML (.rdf), OWL (.owl), N-Triples (.nt), or JSON-LD (.jsonld) file
   - Alternatively, drag and drop your file onto the upload area

2. **Configure validation settings:**

   - Check "Save valid data to dataset" if you want valid data to be stored in the Fuseki database

3. **Validate your data:**

    - Click the "Validate" button
    - The system will process your file and display the validation results

4. **Review validation results:**

    - The system will show whether your data conforms to the TimeRep SHACL shapes
    - If violations are found, they'll appear in the "Violations" tab
    - Warnings are displayed in the "Warnings" tab
    - The "Visualization" tab shows a graphical representation of your RDF data
    - The "Details" tab provides technical information about the validation process

5. **Download validation report:**

   - Click "Download Report" to save the validation results as a JSON file

#### Working with Sample Data

If you don't have your own RDF data, you can generate sample data:

1. **Generate sample data:**

    - Click "Generate Valid Sample" for data that passes validation
    - Click "Generate Invalid Sample" for data with deliberate violations
    - Click "Generate Conflicting Data" to create data that may conflict with existing dataset

2. **Using the conflict generator:**

   - This is a multi-step process:
     - First click generates base valid data - upload and save this to the dataset
     - Second click generates data with direct conflicts with your first upload
     - Subsequent clicks generate random potentially conflicting data

3. **Handling conflicts:**

    - If conflicts are detected, a warning panel will appear
    - You can choose to "Save Anyway" or "Cancel"

#### Working with the Dataset

1. **View dataset statistics:**

    - Click "Load Stats" to view current statistics about the Fuseki dataset
    - This shows how many instances of each TimeRep class exist in the database

2. **Query the dataset:**

    - Click "Query Dataset" to open the SPARQL query panel
    - The default query lists all TimeRep classes and their instance counts
    - Modify the query as needed and click "Run Query"
    - Results appear in a table below the query editor

#### Advanced Usage

- The visualization feature uses vis-network library to display complex RDF relationships
- You can download and modify sample data locally before re-uploading for testing
- Custom SPARQL queries can be used to explore and analyze the TimeRep dataset

This demonstrator is designed to help users validate their data against TimeRep constraints and visualize the structure of their RDF data.