const fs = require('fs');
const path = require('path');

const docsPath = path.join(__dirname, '../docs');
const indexPath = path.join(docsPath, 'index.html');
const scriptPath = path.join(__dirname, 'script.html');
const configPath = path.join(__dirname, 'config.json');
const startPath = path.join(__dirname, 'start.md');

try {
	// Read existing index.html
	let indexContent = fs.readFileSync(indexPath, 'utf8');

	// Read the script tag and inject before </body>
	const scriptContent = fs.readFileSync(scriptPath, 'utf8');
	indexContent = indexContent.replace('</body>', scriptContent + '\n</body>');

	// Read and merge config.json into the existing Docute config
	const configJson = JSON.parse(fs.readFileSync(configPath, 'utf8'));

	// Modify the existing Docute config in index.html
	indexContent = indexContent.replace('})', '}))');
	indexContent = indexContent.replace('new Docute({', 'new Docute(Object.assign(' + JSON.stringify(configJson) + ', {').replace(')});', '}));');

	// Write updated content back
	fs.writeFileSync(indexPath, indexContent, 'utf8');
	console.log('Docute configuration updated successfully.');

	fs.copyFileSync(startPath, path.join(docsPath, 'start.md'));
} catch (error) {
	console.error('Error modifying Docute config:', error);
	process.exit(1);
}
