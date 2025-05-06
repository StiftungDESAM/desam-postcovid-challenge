import Papa from 'papaparse';
import i18n from '@/translations/i18n.js';
const t = i18n.global.t;

self.data = {};

function detectDelimiter(csvString) {
	const lines = csvString.split('\n').slice(0, 5);
	const commaCount = lines.map((line) => line.split(',').length).reduce((a, b) => a + b, 0);
	const semicolonCount = lines.map((line) => line.split(';').length).reduce((a, b) => a + b, 0);

	return commaCount >= semicolonCount ? ',' : ';';
}
self.onmessage = function (e) {
	self.data = e.data;
	const delimiter = detectDelimiter(self.data.fileData);

	Papa.parse(self.data.fileData, {
		delimiter: delimiter,
		header: false,
		skipEmptyLines: false,
		quoteChar: '"',
		escapeChar: '\\',
		dynamicTyping: false,
		newline: '\n',
		comments: false,
		complete: (result) => {
			let lines = result.data;

			if (lines.length < 2) {
				self.postMessage({ type: 'TOAST', data: t('duMinTwoLinesCSV') });
				return;
			}

			const headerRow = lines[0].map((cell) => cell.trim());
			const customClasses = [];

			let columns = [
				{ ref: ['rowID'], text: t('duRowID') },
				...headerRow.map((name, idx) => {
					const customClass = self.functions.getClassForColumn(name);
					if (customClass) {
						customClasses.push({
							className: customClass,
							colRef: name,
							rowRef: null,
						});
					}

					return {
						ref: [name],
						text: `${name} (${self.functions.getTranslationForColumn(name)})`,
						formatter: true,
					};
				}),
			];

			let rows = lines.slice(1).map((row, index) => {
				let obj = { rowID: index + 1 };
				row.forEach((cell, index) => {
					obj[headerRow[index]] = cell.trim();
				});
				return obj;
			});

			self.data.dataTableConfig.data.columns = [];
			self.data.dataTableConfig.data.values = [];
			self.data.tableConfigsForCodeBooks.map((it) => {
				if (it.id == self.data.selectedCodeBook.id) {
					it.tableConfig = JSON.parse(JSON.stringify(self.data.dataTableConfig));
					it.tableConfig.styling = {
						customClasses: customClasses,
					};
					it.tableConfig.data.columns = columns;
					it.tableConfig.data.values = rows;
					it.dataQualityCheckConfig = null;
				}
				return it;
			});
			self.postMessage({ type: 'RESULT', data: JSON.parse(JSON.stringify(self.data.tableConfigsForCodeBooks)) });
		},
		error: (err) => {
			self.postMessage({ type: 'TOAST', data: `${t('duErrorParsingCSV')}: ${err.message}` });
		},
	});
};

self.functions = {
	getClassForColumn: (name) => {
		const refIdx = self.functions.getIdxOfColumn(name);
		return refIdx == -1 ? 'du-column-deleted' : null;
	},
	getTranslationForColumn: (name) => {
		if (self.data.translationColumn) {
			const refIdx = self.functions.getIdxOfColumn(name);
			const columnMapping = self.data.tableConfigsForCodeBooks.find((codeBook) => codeBook.id == self.data.selectedCodeBook.id);
			const translationColumn = columnMapping.data.find(
				(it) => it.tag == columnMapping.mappingColumn || it.assignedItem?.tag == columnMapping.mappingColumn
			);
			return refIdx >= 0 ? translationColumn.rows[refIdx] : '-';
		} else return '-';
	},
	getIdxOfColumn: (ref) => {
		const columnMapping = self.data.tableConfigsForCodeBooks.find((codeBook) => codeBook.id == self.data.selectedCodeBook.id);
		const mappingColumn = columnMapping.mappings.find(
			(it) => it.tag == columnMapping.mappingColumn || it.assignedItem?.tag == columnMapping.mappingColumn
		);
		return mappingColumn.rows.findIndex((it) => it == ref);
	},
};
