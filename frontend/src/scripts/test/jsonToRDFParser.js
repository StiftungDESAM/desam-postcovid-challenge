// import { readFile, writeFile } from 'fs';
const fs = require('fs-extra');

// Function to automatically generate RDF Turtle prefixes based on the JSON content
function generatePrefixes(jsonData) {
	// Start with some common prefixes for RDF
	let prefixes = `
  @prefix ex: <http://example.org/> .
  @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
  @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
  @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
  `;

	// Look through the JSON data to find any other potential prefixes (e.g., for specific vocabularies)
	// This is a simple example, you can extend this part as needed.
	const uniqueLabels = new Set();
	jsonData.forEach((node) => {
		node.n.labels.forEach((label) => uniqueLabels.add(label));
	});

	uniqueLabels.forEach((label) => {
		const prefix = `ex:${label}`;
		prefixes += `@prefix ${label}: <http://example.org/${label}> .\n`;
	});

	return prefixes;
}

// Function to convert the JSON to RDF Turtle format
function jsonToTurtle(jsonData) {
	const prefixes = generatePrefixes(jsonData); // Automatically generate the prefixes

	let rdfTurtle = prefixes;

	jsonData.forEach((node) => {
		const nodeId = node.n.elementId.replace(/:/g, '_'); // Clean up elementId to be valid RDF identifier
		const rdfNode = `ex:${nodeId}`;

		let rdfNodeData = `a ex:${node.n.labels.join(', ex:')} ;\n`;

		// Add properties
		Object.entries(node.n.properties).forEach(([key, value]) => {
			if (typeof value === 'boolean') {
				rdfNodeData += `    ex:${key} "${value}"^^xsd:boolean ;\n`;
			} else if (typeof value === 'number') {
				rdfNodeData += `    ex:${key} "${value}"^^xsd:double ;\n`;
			} else {
				rdfNodeData += `    ex:${key} "${value}" ;\n`;
			}
		});

		// Add the RDF node to the result string
		rdfTurtle += `${rdfNode} ${rdfNodeData.trim()} .\n\n`;
	});

	return rdfTurtle;
}

const rdfData = fs.readFileSync('./ontologyMeta.rdf', 'utf8');

const outputJson = JSON.stringify({ rdf: rdfData }, null, 2);

fs.writeFile('output.json', outputJson, (err) => {
	if (err) console.error('Error writing output file:', err);
	else console.log('RDF Turtle saved to output.json');
});
