import Papa from 'papaparse';
import i18n from '@/translations/i18n.js';
const t = i18n.global.t;

self.data = {};

// delmiter detection for ',' or ';' over the first 5 lines
function detectDelimiter(csvString) {
	const lines = csvString.split('\n').slice(0, 5);
	const commaCount = lines.map((line) => line.split(',').length).reduce((a, b) => a + b, 0);
	const semicolonCount = lines.map((line) => line.split(';').length).reduce((a, b) => a + b, 0);

	return commaCount >= semicolonCount ? ',' : ';';
}

self.onmessage = function (e) {
	self.data = e.data;

	const fileData = self.data.fileData;
	const delimiter = detectDelimiter(fileData);

	Papa.parse(fileData, {
		delimiter: delimiter,
		header: true,
		skipEmptyLines: false,
		quoteChar: '"',
		escapeChar: '\\',
		dynamicTyping: true,
		newline: '\n',
		comments: false,
		complete: (result) => {
			let lines = result.data;

			if (lines.length < 2) {
				self.postMessage({ type: 'TOAST', data: t('cwMinTwoLinesCSV') });
				return;
			}

			let table = lines
				.map((row, index) => {
					let obj = { rowID: index + 1 };

					if (Object.values(row).every((value) => value == null || value === '')) {
						return null;
					}

					Object.keys(row).forEach((key) => {
						obj[key] = row[key];
					});
					return obj;
				})
				.filter((row) => row != null);

			self.postMessage({ type: 'RESULT', data: table });
		},
		error: (err) => {
			self.postMessage({ type: 'TOAST', data: `${t('clErrorParsingCSV')}: ${err.message}` });
		},
	});
};
