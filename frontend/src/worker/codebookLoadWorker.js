import Papa from 'papaparse';
import i18n from '@/translations/i18n.js';
const t = i18n.global.t;

self.data = {};

self.onmessage = function (e) {
	self.data = e.data;

	// CSV Parsing
	Papa.parse(self.data.fileData, {
		delimiter: ',',
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
