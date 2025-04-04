import { DATA_QUALITY_CHECK_MODE } from '@/enums/enums';

// Datatype checking
const NUMBER_TYPES_DE = ['zahl', 'ganzzahl', 'kommazahl'];
const NUMBER_TYPES = ['number', 'int', 'long', 'double', 'float', ...NUMBER_TYPES_DE];
const STRING_TYPES_DE = ['satz', 'zeichenkette', 'wort', 'zeichen', 'buchstabe'];
const STRING_TYPES = ['string', 'str', 'char', 'text', ...STRING_TYPES_DE];
const BOOLEAN_TYPES_DE = [];
const BOOLEAN_TYPES = ['boolean', 'bool', ...BOOLEAN_TYPES_DE];
const TRUE_FALSE_TYPES_DE = ['wahr', 'ja', 'falsch', 'nein'];
const TRUE_FALSE_TYPES = ['true', '1', 'false', '0', ...TRUE_FALSE_TYPES_DE];
const DATE_TYPES_DE = ['datum', 'zeit', 'uhrzeit', 'zeitstempel'];
const DATE_TYPES = ['date', 'time', 'datetime', 'timestamp', ...DATE_TYPES_DE];
const ARRAY_TYPES_DE = [];
const ARRAY_TYPES = ['array', 'list', 'vector', 'tuple', ...ARRAY_TYPES_DE];
const OBJECT_TYPES_DE = [];
const OBJECT_TYPES = ['object', 'dict', 'map', 'record', 'struct', 'hashmap', 'json', ...OBJECT_TYPES_DE];

// Required checking
// prettier-ignore
const REQUIRED_TYPES_DE = ['erforderlich', 'notwendig', 'verpflichtend', 'pflicht', 'muss', 'benötigt', 'obligatorisch', 'zwingend', 'ja', 'ein', 'aktiv', 'einschalten'];
const REQUIRED_TYPES = ['true', '1', 'yes', 'y', 'required', 'on', 'enable', 'mandatory', 'must', ...REQUIRED_TYPES_DE];

self.checkResult = {
	errors: [],
	warnings: [],
	info: [],
};

self.onmessage = function (e) {
	const start = performance.now();
	const config = e.data.config;
	const codeBook = e.data.codeBook;
	const mode = e.data.mode;

	self.functions.loopThroughCells(config, codeBook, mode, (data, config, refIdx, value, colRef, rowRef, meta) => {
		self.functions.checkValueType(mode, data, config, refIdx, value, colRef, rowRef, meta);
		self.functions.checkValueRangeMin(mode, data, config, refIdx, value, colRef, rowRef, meta);
		self.functions.checkValueRangeMax(mode, data, config, refIdx, value, colRef, rowRef, meta);
		self.functions.checkValueMapping(mode, data, config, refIdx, value, colRef, rowRef, meta);
		// self.functions.checkValueBranching(mode, data, config, refIdx, value, colRef, rowRef, meta);
		self.functions.checkValueRequired(mode, data, config, refIdx, value, colRef, rowRef, meta);
	});

	if (config.EMPTY_ROWS) self.functions.checkForEmptyRows(mode, codeBook);
	if (config.EMPTY_COLUMNS) self.functions.checkForEmptyColumns(mode, codeBook);
	if (config.EMPTY_VALUES) self.functions.checkForEmptyValues(mode, codeBook);

	self.checkResult.errors = self.functions.removeDuplications(self.checkResult.errors);
	self.checkResult.warnings = self.functions.removeDuplications(self.checkResult.warnings);
	self.checkResult.info = self.functions.removeDuplications(self.checkResult.info);

	self.checkResult.info.push({
		text: 'EXECUTION_DURATION',
		textOptions: {
			duration: ((performance.now() - start) / 1000).toFixed(3),
		},
	});
	self.postMessage(self.checkResult);
};

self.functions = {
	loopThroughCells: (config, data, mode, cb) => {
		if (mode == DATA_QUALITY_CHECK_MODE.UPLOAD) {
			data.tableConfig.data.columns.forEach((col, idx) => {
				const colRef = col.ref.join('');
				const refIdx = data.mappings[0].rows.findIndex((it) => it == colRef);

				// Only loop through columns that are included in the codebook
				if (refIdx != -1)
					data.tableConfig.data.values.forEach((row) => cb(data, config, refIdx, row[colRef], colRef, row[data.tableConfig.data.key]));
			});
		} else {
			data.data.forEach((item) => {
				item.answers.forEach((ans, idx) =>
					cb(data, config, null, ans.toString(), item.itemMeta[data.usedIdentifier], idx + 1, item.itemMeta)
				);
			});
		}
	},
	checkValueType: (mode, data, config, refIdx, value, colRef, rowRef, meta) => {
		let compareValue = null;
		let valueType = null;
		let linkedData = null;

		try {
			if (mode == DATA_QUALITY_CHECK_MODE.UPLOAD) {
				valueType = data.data.find((it) => it.id.toString() == config.VALUE_TYPE);
				linkedData = data.linkedData[refIdx];
				compareValue =
					linkedData && valueType.assignedMetaField && linkedData[valueType.assignedMetaField.name]
						? linkedData[valueType.assignedMetaField.name]?.toLowerCase()
						: valueType.rows[refIdx]?.toLowerCase();
			} else compareValue = meta[config.VALUE_TYPE]?.toLowerCase();

			if (NUMBER_TYPES.includes(compareValue)) {
				if (isNaN(value) || value.trim() == '') throw 'WRONG_DATATYPE';
			} else if (STRING_TYPES.includes(compareValue)) {
				if (typeof value !== 'string') throw 'WRONG_DATATYPE';
			} else if (BOOLEAN_TYPES.includes(compareValue)) {
				const lowerCaseValue = value.toString()?.toLowerCase();
				if (!TRUE_FALSE_TYPES.includes(lowerCaseValue) && typeof value !== 'boolean') throw 'WRONG_DATATYPE';
			} else if (DATE_TYPES.includes(compareValue)) {
				if (isNaN(Date.parse(value))) throw 'WRONG_DATATYPE';
			} else if (ARRAY_TYPES.includes(compareValue)) {
				const parsed = JSON.parse(value);
				if (!Array.isArray(parsed)) throw 'WRONG_DATATYPE';
			} else if (OBJECT_TYPES.includes(compareValue)) {
				const parsed = JSON.parse(value);
				if (typeof parsed !== 'object' || Array.isArray(parsed) || parsed === null) throw 'WRONG_DATATYPE';
			} else if (compareValue != '') throw 'UNKNOWN_DATATYPE';
		} catch (error) {
			if (value && value != '') {
				const checkResult = {
					text: typeof error == 'string' ? error : 'UNKNOWN_ERROR',
					textOptions: {
						value: value,
						foundType: typeof value,
						requiredType: compareValue,
						error: error,
					},
					colRef: colRef,
					rowRef: rowRef,
				};
				self.checkResult.errors.push(checkResult);
			}
		}
	},
	checkValueRangeMin: (mode, data, config, refIdx, value, colRef, rowRef, meta) => {
		let minValue = null;
		let valueRangeMin = null;
		let linkedData = null;

		try {
			if (mode == DATA_QUALITY_CHECK_MODE.UPLOAD) {
				valueRangeMin = data.data.find((it) => it.id.toString() == config.VALUE_RANGE_MIN);
				linkedData = data.linkedData[refIdx];
				minValue =
					linkedData && valueRangeMin.assignedMetaField && linkedData[valueRangeMin.assignedMetaField.name]
						? linkedData[valueRangeMin.assignedMetaField.name]?.toString()
						: valueRangeMin.rows[refIdx]?.toString();
			} else minValue = meta[config.VALUE_RANGE_MIN]?.toString();

			if (!isNaN(minValue) && minValue != '') {
				if (!isNaN(value)) {
					if (Number(value) < Number(minValue)) throw 'OUT_OF_RANGE_MIN';
				} else throw 'INVALID_VALUE_MIN';
			} else if (minValue && minValue != '') throw 'INVALID_MIN_VALUE';
		} catch (error) {
			const checkResult = {
				text: typeof error == 'string' ? error : 'UNKNOWN_ERROR',
				textOptions: {
					value: value,
					minValue: minValue,
					error: error,
				},
				colRef: colRef,
				rowRef: rowRef,
			};

			self.checkResult.errors.push(checkResult);
		}
	},
	checkValueRangeMax: (mode, data, config, refIdx, value, colRef, rowRef, meta) => {
		let valueRangeMax = null;
		let linkedData = null;
		let maxValue = null;

		try {
			if (mode == DATA_QUALITY_CHECK_MODE.UPLOAD) {
				valueRangeMax = data.data.find((it) => it.id.toString() == config.VALUE_RANGE_MAX);
				linkedData = data.linkedData[refIdx];
				maxValue =
					linkedData && valueRangeMax.assignedMetaField && linkedData[valueRangeMax.assignedMetaField.name]
						? linkedData[valueRangeMax.assignedMetaField.name]?.toString()
						: valueRangeMax.rows[refIdx]?.toString();
			} else maxValue = meta[config.VALUE_RANGE_MAX]?.toString();

			if (!isNaN(maxValue) && maxValue != '') {
				if (!isNaN(value)) {
					if (Number(value) > Number(maxValue)) throw 'OUT_OF_RANGE_MAX';
				} else throw 'INVALID_VALUE_MAX';
			} else if (maxValue && maxValue != '') throw 'INVALID_MAX_VALUE';
		} catch (error) {
			const checkResult = {
				text: typeof error == 'string' ? error : 'UNKNOWN_ERROR',
				textOptions: {
					value: value,
					maxValue: maxValue,
					error: error,
				},
				colRef: colRef,
				rowRef: rowRef,
			};

			self.checkResult.errors.push(checkResult);
		}
	},
	checkValueMapping: (mode, data, config, refIdx, value, colRef, rowRef, meta) => {
		let mappingValue = null;
		let mappings = null;
		let linkedData = null;
		let linkedMappingValues = '';
		let originalMappingValues = '';
		try {
			if (value && value != '') {
				if (mode == DATA_QUALITY_CHECK_MODE.UPLOAD) {
					mappings = data.data.find((it) => it.id.toString() == config.VALUE_MAPPING);
					linkedData = data.linkedData[refIdx];
					linkedMappingValues =
						linkedData && mappings.assignedMetaField && linkedData[mappings.assignedMetaField.name]
							? linkedData[mappings.assignedMetaField.name]
							: [];
					originalMappingValues = mappings.rows[refIdx];
				} else linkedMappingValues = meta[config.VALUE_MAPPING];

				const answeredValues = value?.split(self.functions.getSeparator(config.answerSeparator)).map((it) => it.trim()) || [];
				let error = false;

				// Checking answers by linked data
				if (linkedMappingValues && linkedMappingValues != '') {
					mappingValue = linkedMappingValues.split(self.functions.getSeparator(config.mappingSeparator)).map((it) => it.trim());
					answeredValues.forEach((answer) => {
						if (!mappingValue.includes(answer)) error = true;
					});

					// Fallback to split by ,
					if (mappingValue.length == 1) {
						error = false;
						mappingValue = linkedMappingValues.split(',').map((it) => it.trim());
						answeredValues.forEach((answer) => {
							if (!mappingValue.includes(answer)) error = true;
						});
					}
				}

				// Using original mapping if no linked data is available
				if ((!linkedMappingValues || linkedMappingValues == '' || error) && originalMappingValues && originalMappingValues != '') {
					mappingValue = originalMappingValues.split(self.functions.getSeparator(config.mappingSeparator)).map((it) => it.trim());
					answeredValues.forEach((val) => {
						if (!mappingValue.includes(val)) throw 'WRONG_MAPPING';
					});
				} else if (error) throw 'WRONG_MAPPING';
			}
		} catch (error) {
			const checkResult = {
				text: typeof error == 'string' ? error : 'UNKNOWN_ERROR',
				textOptions: {
					value: value,
					requiredValues: mode == DATA_QUALITY_CHECK_MODE.UPLOAD ? mappingValue.join(', ') : meta[config.VALUE_MAPPING],
					error: error,
				},
				colRef: colRef,
				rowRef: rowRef,
			};

			self.checkResult.errors.push(checkResult);
		}
	},
	getSeparator: (mappingSeparator) => {
		const separators = {
			COMMA: ',',
			SEMICOLON: ';',
			DASH: '-',
			UNDERSCORE: '_',
			SLASH: '/',
			COLON: ':',
			DOT: '.',
			BAR: '|',
		};

		return separators[mappingSeparator] || ',';
	},
	checkValueBranching: (mode, data, config, refIdx, value, colRef, rowRef, meta) => {
		let branchingValue = null;
		let lastValue = null;
		try {
			const branchingType = data.data.find((it) => it.id.toString() == config.VALUE_BRANCHING);
			const linkedData = data.linkedData[refIdx];
			const linkedBranchingValue =
				linkedData && branchingType.assignedMetaField && linkedData[branchingType.assignedMetaField.name]
					? linkedData[branchingType.assignedMetaField.name]
					: null;
			const originalBranchingValue = branchingType.rows[refIdx];

			let error = null;
			[linkedBranchingValue, originalBranchingValue].forEach((it, idx) => {
				branchingValue = it;
				if (branchingValue && branchingValue != '') {
					const lastRef = data.mappings[0].rows[refIdx - 1];
					lastValue = data.tableConfig.data.values.find((it) => it[data.tableConfig.data.key] == rowRef)[lastRef];

					if (config.branchIdentifier == 'ONLY_NUMBER') {
						const numberMatch = branchingValue.match(/\b\d+(\.\d+)?\b/);

						if (!numberMatch) error = 'NO_MATCHING_NUMBER';
						else {
							const regex = new RegExp(`\\b${numberMatch[0]}\\b`);
							if (!regex.test(lastValue)) error = 'FORBIDDEN_ANSWER';
						}
					} else if (config.branchIdentifier == 'ONLY_TEXT') {
						const cleanedInputString = branchingValue
							.replace(/\d+(\.\d+)?/g, '')
							.trim()
							.replace(/[.*+?^=!:${}()|\[\]\/\\]/g, '\\$&');
						const cleanedAnswerOptions = lastValue.replace(/\d+(\.\d+)?/g, '').trim();

						const regex = new RegExp(`\\b${cleanedInputString}\\b`, 'i');
						if (!regex.test(cleanedAnswerOptions)) error = 'FORBIDDEN_ANSWER';
					} else if (config.branchIdentifier == 'FULL_TEXT' && branchingValue != lastValue) error = 'FORBIDDEN_ANSWER';
				}
			});
			if (error) throw error;
		} catch (error) {
			const checkResult = {
				text: typeof error == 'string' ? error : 'UNKNOWN_ERROR',
				textOptions: {
					value: value,
					lastValue: lastValue,
					branchingValue: branchingValue,
					error: error,
				},
				colRef: colRef,
				rowRef: rowRef,
			};

			self.checkResult.errors.push(checkResult);
		}
	},
	checkValueRequired: (mode, data, config, refIdx, value, colRef, rowRef, meta) => {
		let requiredType = null;
		let linkedData = null;
		let requiredValue = null;

		try {
			if (mode == DATA_QUALITY_CHECK_MODE.UPLOAD) {
				requiredType = data.data.find((it) => it.id.toString() == config.VALUE_REQUIRED);
				linkedData = data.linkedData[refIdx];
				requiredValue =
					linkedData && requiredType.assignedMetaField && linkedData[requiredType.assignedMetaField.name]
						? linkedData[requiredType.assignedMetaField.name]?.toString().toLowerCase()
						: requiredType.rows[refIdx]?.toString().toLowerCase();
			} else requiredValue = meta[config.VALUE_REQUIRED]?.toString().toLowerCase();

			if (REQUIRED_TYPES.includes(requiredValue) && (!value || value == '' || value == null || value == undefined)) throw 'REQUIRED_MISSING';
		} catch (error) {
			const checkResult = {
				text: typeof error == 'string' ? error : 'UNKNOWN_ERROR',
				textOptions: {
					error: error,
				},
				colRef: colRef,
				rowRef: rowRef,
			};

			self.checkResult.errors.push(checkResult);
		}
	},
	checkForEmptyValues: (mode, data) => {
		data.tableConfig.data.columns.forEach((col, idx) => {
			const colRef = col.ref.join('');
			const refIdx = data.mappings[0].rows.findIndex((it) => it == colRef);

			// Only loop through columns that are included in the codebook
			if (refIdx != -1) {
				data.tableConfig.data.values.forEach((row) => {
					if (self.functions.valueIsNotAvailable(row[colRef], true, false)) {
						self.checkResult.warnings.push({
							text: 'EMPTY_CELL',
							colRef: colRef,
							rowRef: row[data.tableConfig.data.key],
						});
					}
				});
			}
		});

		if (!self.checkResult.warnings.find((it) => it.text == 'EMPTY_CELL')) {
			self.checkResult.info.push({
				text: 'NO_EMPTY_CELLS',
			});
		}
	},
	checkForEmptyRows: (mode, data) => {
		data.tableConfig.data.values.forEach((row) => {
			if (Object.values(row).filter((cell) => !cell).length == Object.values(row).length - 1) {
				self.checkResult.warnings.push({
					text: 'EMPTY_ROW',
					colRef: null,
					rowRef: row[data.tableConfig.data.key],
				});
			}
		});

		if (!self.checkResult.warnings.find((it) => it.text == 'EMPTY_ROW')) {
			self.checkResult.info.push({
				text: 'NO_EMPTY_ROWS',
			});
		}
	},
	checkForEmptyColumns: (mode, data) => {
		let dataPerColumn = {};

		data.tableConfig.data.columns.forEach((col, idx) => {
			const colRef = col.ref.join('');
			const refIdx = data.mappings[0].rows.findIndex((it) => it == colRef);

			// Only loop through columns that are included in the codebook
			if (refIdx != -1) {
				data.tableConfig.data.values.forEach((row) => {
					const cell = row[colRef];
					if (cell && dataPerColumn[colRef]) dataPerColumn[colRef].push(cell);
					else if (cell && !dataPerColumn[colRef]) dataPerColumn[colRef] = [cell];
					else if (!cell && !dataPerColumn[colRef]) dataPerColumn[colRef] = [];
				});
			}
		});

		Object.keys(dataPerColumn).forEach((key) => {
			if (dataPerColumn[key].length == 0) {
				self.checkResult.warnings.push({
					text: 'EMPTY_COLUMN',
					colRef: key,
					rowRef: null,
				});
			}
		});

		if (!self.checkResult.warnings.find((it) => it.text == 'EMPTY_COLUMN')) {
			self.checkResult.info.push({
				text: 'NO_EMPTY_COLUMNS',
			});
		}
	},
	valueIsNotAvailable: (value, includeEmptyString = false, includeZero = false) => {
		const isNullOrUndefined = value == null;
		const isEmpty = value === '';
		const isZero = value === 0;

		return isNullOrUndefined || (includeEmptyString && isEmpty) || (includeZero && isZero);
	},
	removeDuplications: (data) => {
		return data.reduce(
			(acc, obj) => {
				let key = `${obj.text}-${obj.rowRef}-${obj.colRef}`;
				if (obj.textOptions) {
					Object.keys(obj.textOptions)
						.sort()
						.forEach((it) => {
							key += `-${obj.textOptions[it]}`;
						});
				}

				if (!acc.set.has(key)) {
					acc.set.add(key);
					acc.result.push(obj);
				}
				return acc;
			},
			{ set: new Set(), result: [] }
		).result;
	},
};
