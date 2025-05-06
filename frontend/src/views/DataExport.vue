<template>
	<div class="de-wrap-content">
		<h1>{{ $t('deDataExport') }}</h1>
		<em>{{ $t('deDataExportExplanation') }}</em>
		<div class="de-wrap-meta-viewer">
			<OntologyViewer :rdfData="ontologyData" @selectElement="selectElement" />
		</div>
		<div class="de-wrap-search-bar">
			<div class="de-selected-meta-element">
				<p v-if="!selectedElement">{{ $t('deNoItemSelected') }}</p>
				<div v-else class="de-leaf-node">{{ selectedElement.data.name }}</div>
			</div>
			<div class="de-search-bar">
				<input
					type="text"
					v-model="searchText"
					:placeholder="$t('deSearchSelectedMetaFields')"
					@keyup.enter="canSearch ? searchForItems() : null"
				/>
				<div class="de-input-search-options">
					<span
						:title="$t('deCaseSensitiv')"
						:class="caseSensitive ? 'de-selected-search-option' : ''"
						@click="caseSensitive = !caseSensitive"
						>Aa</span
					>
					<span
						:title="$t('deMatchFullText')"
						:class="matchFullText ? 'de-selected-search-option' : ''"
						@click="matchFullText = !matchFullText"
						>ab</span
					>
				</div>
				<button :class="canSearch ? 'app-default-btn' : 'app-disabled-btn'" @click="searchForItems">
					{{ $t('deSearchOntology') }} <fai v-if="!isSearching" icon="fas fa-magnifying-glass" />
					<fai v-else icon="fas fa-spinner" class="de-loading-spinner" />
				</button>
			</div>
		</div>
		<div class="de-wrap-searched-items-table">
			<h2>{{ $t('deFoundData') }}</h2>
			<em>{{ $t('deFoundDataSelectExplanation') }}</em>
			<div class="de-searched-items-table">
				<LoadingSpinner v-if="isSearching" :wrapperClass="'de-searched-items-table'" />
				<Table :config="searchedTableConfig" @selectItem="selectSearchedItem" :resetSelected="resetSelectedSearch" />
			</div>
			<div class="de-wrap-button">
				<button :class="selectedSearchedItems.length > 0 ? 'app-default-btn' : 'app-disabled-btn'" @click="addSearchedItemsToSelected">
					{{ $t('deSelectItems', { amount: selectedSearchedItems.length }) }}
				</button>
			</div>
		</div>
		<div class="de-wrap-selected-items-table">
			<h2>{{ $t('deSelectedData') }}</h2>
			<em>{{ $t('deSelectedDataDeselectExplanation') }}</em>
			<div class="de-selected-items-table">
				<LoadingSpinner v-if="false" :wrapperClass="'de-selected-items-table'" />
				<Table :config="selectedTableConfig" @selectItem="selectSelectedItem" :resetSelected="resetSelectedSelected" />
			</div>
			<div class="de-wrap-button">
				<button :class="selectedSelectedItems.length > 0 ? 'app-default-btn' : 'app-disabled-btn'" @click="removeSelectedItems">
					{{ $t('deDeselectItems', { amount: selectedSelectedItems.length }) }}
				</button>
			</div>
		</div>
		<div class="de-wrap-export-options">
			<h2>{{ $t('deExportConfiguration') }}</h2>
			<div class="de-wrap-export-option">
				<label>{{ $t('deFileName') }}</label>
				<input type="text" v-model="exportConfig.fileName" :placeholder="$t('deFileName')" required />
			</div>
			<div class="de-wrap-export-option">
				<label>{{ $t('deFileType') }}</label>
				<select v-model="exportConfig.fileType" required>
					<option value="" disabled selected hidden>{{ $t('deSelectFileType') }}</option>
					<option :value="typeEnum.CSV">{{ $t('deCsvType') }}</option>
					<option :value="typeEnum.JSON">{{ $t('deJsonType') }}</option>
				</select>
			</div>
			<div class="de-wrap-export-option">
				<label>{{ $t('deIdentificator') }}</label>
				<select v-model="exportConfig.identificator" required>
					<option value="" disabled selected hidden>{{ $t('deSelectIdentificator') }}</option>
					<option v-if="validIdentificators.length == 0" :value="null" disabled>{{ $t('deNoIdentificatorsAvailable') }}</option>
					<option v-for="identificator in validIdentificators" :key="identificator.tag" :value="identificator.tag">
						{{ identificator.name }}
					</option>
				</select>
			</div>
			<div class="de-wrap-export-option">
				<label>{{ $t('deSeparator') }}</label>
				<select v-model="exportConfig.separator" required>
					<option value="" disabled selected hidden>{{ $t('dqcSelectSplittingMethod') }}</option>
					<option :value="splitEnum.COMMA">{{ $t('dqcSplitByComma') }} (,)</option>
					<option :value="splitEnum.SEMICOLON">{{ $t('dqcSplitBySemicolon') }} (;)</option>
					<option :value="splitEnum.DASH">{{ $t('dqcSplitByDash') }} (-)</option>
					<option :value="splitEnum.UNDERSCORE">{{ $t('dqcSplitByUnderscore') }} (_)</option>
					<option :value="splitEnum.SLASH">{{ $t('dqcSplitBySlash') }} (/)</option>
					<option :value="splitEnum.COLON">{{ $t('dqcSplitByColon') }} (:)</option>
					<option :value="splitEnum.DOT">{{ $t('dqcSplitByDot') }} (.)</option>
					<option :value="splitEnum.BAR">{{ $t('dqcSplitByBar') }} (|)</option>
				</select>
			</div>
			<div class="de-wrap-export-checkbox">
				<input id="includeMeta" type="checkbox" v-model="exportConfig.includeMeta" />
				<label for="includeMeta">{{ $t('deExportMeta') }}</label>
			</div>
		</div>
		<div class="de-wrap-button">
			<button :class="canExport ? 'app-success-btn' : 'app-disabled-btn'" @click="exportData">
				{{ $t('deExportData') }} <fai icon="fas fa-download" />
			</button>
		</div>
	</div>
</template>

<script>
import OntologyViewer from '@/components/ontology/OntologyViewer.vue';
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
import Table from '@/components/general/Table.vue';
import Papa from 'papaparse';
import JSZip from 'jszip';
import { searchedTableConfig } from '@/components/export/searchedTableConfig';
import { selectedTableConfig } from '@/components/export/selectedTableConfig';
import { FILE_TYPE, MAPPING_SPLIT, ONTOLOGY_ELEMENT, TOAST_TYPE } from '@/enums/enums';
/**
 * @vuese
 * @group DataExport
 * Provides data export functionality to the user
 */
export default {
	name: 'DataExport',
	components: { OntologyViewer, Table, LoadingSpinner },
	emits: [],
	props: {},
	watch: {},
	setup() {
		const typeEnum = FILE_TYPE;
		const splitEnum = MAPPING_SPLIT;
		return { typeEnum, splitEnum };
	},
	data() {
		return {
			resetSelectedSearch: false,
			resetSelectedSelected: false,
			ontologyData: null,
			isSearching: false,
			isExporting: false,
			selectedElement: null,
			searchText: null,
			caseSensitive: false,
			matchFullText: false,
			uniqueMetaFields: {},
			searchedTableConfig: searchedTableConfig,
			selectedTableConfig: selectedTableConfig,
			selectedSearchedItems: [],
			selectedSelectedItems: [],
			exportConfig: {
				fileName: '',
				fileType: '',
				identificator: '',
				separator: '',
				includeMeta: true,
			},
		};
	},
	computed: {
		canSearch() {
			return this.selectedElement && !this.isSearching && this.searchText?.length > 0;
		},
		validIdentificators() {
			let validIdentificators = [];

			if (this.selectedTableConfig.data.values.length > 0) {
				Object.keys(this.uniqueMetaFields).forEach((key) => {
					if (!['amountAnswers'].includes(key)) {
						const data = new Set(this.selectedTableConfig.data.values.map((it) => it[key]));
						if (data.size == this.selectedTableConfig.data.values.length) validIdentificators.push({ ...this.uniqueMetaFields[key] });
					}
				});
			}

			return validIdentificators;
		},
		canExport() {
			return (
				this.exportConfig.fileName &&
				this.exportConfig.fileType &&
				this.exportConfig.identificator &&
				(this.exportConfig.separator || this.exportConfig.fileType == FILE_TYPE.JSON) &&
				this.selectedTableConfig.data.values.length > 0 &&
				!this.isExporting
			);
		},
	},
	created() {
		this.getMetaOntology();
	},
	mounted() {},
	beforeDestroy() {},
	methods: {
		getMetaOntology() {
			this.$network.getData(`/api/ontology/meta?query_type=rdf`, null, null, (err, data) => {
				try {
					if (!err) this.ontologyData = data.rdf;
					else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.isLoading = false;
					window.dispatchEvent(new Event('resize'));
				}
			});
		},
		selectElement(item) {
			if (item?.from == ONTOLOGY_ELEMENT.LEAF) this.selectedElement = item;
			else this.selectedElement = null;
		},
		searchForItems() {
			if (!this.isSearching) {
				this.isSearching = true;
				this.selectedSearchedItems = [];
				this.resetSelectedSearch = !this.resetSelectedSearch;

				const params = `tag=${this.selectedElement.data.tag}&search=${this.searchText}&case_sensitive=${this.caseSensitive}&match_full_text=${this.matchFullText}`;

				this.$network.getData(`/api/data/search?${params}`, null, null, (err, data) => {
					try {
						if (!err) this.fillSearchedTable(data);
						else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
					} catch (error) {
						console.log(error);
						this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
					} finally {
						this.isSearching = false;
					}
				});
			}
		},
		fillSearchedTable(data) {
			this.searchedTableConfig.data.columns = [];
			this.searchedTableConfig.data.values = [];

			const { columns: columns, rows: rows } = this.computeColumnsAndRows(data);

			this.$nextTick(() => {
				this.searchedTableConfig.data.columns = columns;
				this.searchedTableConfig.data.values = rows;

				window.scrollTo({
					top: document.querySelector('.de-wrap-searched-items-table').offsetTop - 10,
					behavior: 'smooth',
				});
			});
		},
		computeColumnsAndRows(data) {
			if (data.length > 0) {
				let columns = [];
				let rows = [];
				let uniqueMetaFields = {
					id: { name: this.$t('deRowID'), tag: 'META_ROW_ID' },
					amountAnswers: { name: this.$t('deAmountData') },
				};

				data.forEach((it) => {
					Object.keys(it.itemMeta).forEach((key) => {
						if (!uniqueMetaFields[key]) uniqueMetaFields[key] = it.itemMeta[key];
					});
				});

				this.uniqueMetaFields = uniqueMetaFields;

				const keys = Object.keys(uniqueMetaFields);

				keys.forEach((key) => {
					columns.push({
						ref: [key],
						text: uniqueMetaFields[key].name,
						formatter: (value) => {
							return this.$global.valueIsNotAvailable(value, true, false) ? '-' : value;
						},
					});
				});

				data.forEach((it) => {
					let row = {};
					keys.forEach((key) => {
						if (!this.$global.valueIsNotAvailable(it.itemMeta[key]?.value, true, false)) row[key] = it.itemMeta[key].value;
						else row[key] = '';
					});

					row.id = it.id;
					row.amountAnswers = it.amountAnswers;

					rows.push(row);
				});

				const index = columns.findIndex((item) => item.ref.join('') == 'id');
				if (index > -1) {
					const [element] = columns.splice(index, 1);
					columns.unshift(element);
				}

				return { columns: columns, rows: rows };
			} else return { columns: [], rows: [] };
		},
		selectSearchedItem(item) {
			let itemExists = this.selectedSearchedItems.some((it) => it.id == item.id);
			if (itemExists) this.selectedSearchedItems = this.selectedSearchedItems.filter((it) => it.id != item.id);
			else this.selectedSearchedItems.push(item);
		},
		addSearchedItemsToSelected() {
			this.selectedSelectedItems = [];
			let columns = [];
			let rows = [];
			const existingColumns = this.selectedTableConfig.data.columns || [];
			const existingRows = this.selectedTableConfig.data.values || [];

			const existingKeys = new Set();

			existingColumns.forEach((it) => {
				existingKeys.add(it.ref.join(''));
			});

			this.selectedSearchedItems.forEach((it) => {
				Object.keys(it).forEach((key) => existingKeys.add(key));
			});

			existingKeys.forEach((key) => {
				columns.push({
					ref: [key],
					text: this.uniqueMetaFields[key].name,
					formatter: (value) => {
						return this.$global.valueIsNotAvailable(value, true, false) ? '-' : value;
					},
				});
			});

			let usedItems = [];
			[...existingRows, ...this.selectedSearchedItems].forEach((it) => {
				if (!usedItems.includes(it.id)) {
					let row = {};
					existingKeys.forEach((key) => {
						if (!this.$global.valueIsNotAvailable(it[key], true, false)) row[key] = it[key];
						else row[key] = '';
					});

					row.id = it.id;
					row.amountAnswers = it.amountAnswers;

					usedItems.push(it.id);
					rows.push(row);
				}
			});

			rows = rows.sort((a, b) => a.id - b.id);

			const index = columns.findIndex((item) => item.ref.join('') == 'id');
			if (index > -1) {
				const [element] = columns.splice(index, 1);
				columns.unshift(element);
			}

			this.selectedTableConfig.data.columns = [];
			this.selectedTableConfig.data.values = [];

			this.selectedSearchedItems = [];
			this.resetSelectedSearch = !this.resetSelectedSearch;
			this.resetSelectedSelected = !this.resetSelectedSelected;

			this.$nextTick(() => {
				this.selectedTableConfig.data.columns = columns;
				this.selectedTableConfig.data.values = rows;

				window.scrollTo({
					top: document.querySelector('.de-wrap-selected-items-table').offsetTop - 10,
					behavior: 'smooth',
				});
			});
		},
		selectSelectedItem(item) {
			let itemExists = this.selectedSelectedItems.some((it) => it.id == item.id);
			if (itemExists) this.selectedSelectedItems = this.selectedSelectedItems.filter((it) => it.id != item.id);
			else this.selectedSelectedItems.push(item);
		},
		removeSelectedItems() {
			const itemsToRemove = this.selectedSelectedItems.map((it) => it.id);
			this.selectedTableConfig.data.values = this.selectedTableConfig.data.values.filter((it) => !itemsToRemove.includes(it.id));
			if (this.selectedTableConfig.data.values.length == 0) this.selectedTableConfig.data.columns = [];
			this.selectedSelectedItems = [];
		},
		exportData() {
			if (!this.isExporting) {
				this.isExporting = true;

				const params = `file_name=${this.exportConfig.fileName}&file_type=${this.exportConfig.fileType}&separator=${this.exportConfig.separator}&identificator=${this.exportConfig.identificator}&items=${this.selectedTableConfig.data.values.map((it) => it.id).join(',')}`;
				this.$network.getData(`/api/data/export?${params}`, null, null, (err, data) => {
					try {
						if (!err) this.handleExportedData(data);
						else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
					} catch (error) {
						this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
					} finally {
						this.isExporting = false;
					}
				});
			}
		},
		async handleExportedData(data) {
			const zip = new JSZip();

			this.generateExportFile(data, zip);
			if (this.exportConfig.includeMeta) this.generateMetaFile(zip);

			const zipBlob = await zip.generateAsync({ type: 'blob' });

			const link = document.createElement('a');
			link.href = URL.createObjectURL(zipBlob);
			link.download = `${this.exportConfig.fileName}.zip`;
			link.click();

			this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('deDataExportSuccessfull'));
		},
		generateExportFile(data, zip) {
			if (this.exportConfig.fileType == FILE_TYPE.CSV) zip.file(`${this.exportConfig.fileName}.csv`, data.csv);
			else if (this.exportConfig.fileType == FILE_TYPE.JSON) zip.file(`${this.exportConfig.fileName}.json`, JSON.stringify(data.data || {}));
		},
		generateMetaFile(zip) {
			if (this.exportConfig.fileType == FILE_TYPE.CSV) {
				const csvData = Papa.unparse(this.selectedTableConfig.data.values, { delimiter: this.getSeparator() });
				zip.file(`${this.exportConfig.fileName}_meta.csv`, csvData);
			} else if (this.exportConfig.fileType == FILE_TYPE.JSON) {
				zip.file(`${this.exportConfig.fileName}_meta.json`, JSON.stringify(this.selectedTableConfig.data.values));
			}
		},
		getSeparator() {
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

			return separators[this.exportConfig.separator] || ';';
		},
	},
};
</script>

<style scoped>
.de-wrap-content {
	width: 100%;
	position: relative;
	margin-bottom: 20px;
}

.de-wrap-content h1 {
	margin-bottom: 10px;
}

.de-wrap-content h2 {
	margin: 20px 0px 10px 0px;
	text-decoration: underline;
	font-weight: normal;
}

.de-wrap-content em {
	display: inline-block;
	margin-bottom: 10px;
}

.de-wrap-meta-viewer {
	width: 100%;
	height: 80vh;
	margin: 10px 2px;
	position: relative;
	overflow: hidden;
	border: 1px solid var(--main-color-light);
	box-sizing: border-box;
}

.de-wrap-search-bar {
	width: 100%;
	height: 50px;
	margin: 0px 2px;
	display: flex;
	justify-content: center;
	align-items: stretch;
	box-sizing: border-box;
	border: 1px solid var(--main-color-light);
}

.de-selected-meta-element {
	flex: 1 1;
	min-width: fit-content;
	padding: 5px 10px;
	display: flex;
	justify-content: center;
	align-items: center;
	border-right: 1px solid var(--main-color-light);
}

.de-search-bar {
	flex: 1 1 calc(100% - 200px);
	padding: 5px;
	display: flex;
	justify-content: center;
	align-items: stretch;
	gap: 5px;
	position: relative;
}

.de-search-bar input {
	flex: 1 1 calc(100% - 250px);
	height: 40px;
	padding: 5px 55px 5px 10px;
	font-size: 16px;
}

.de-input-search-options {
	width: fit-content;
	height: 36px;
	padding-left: 2px;
	position: absolute;
	right: 260px;
	top: 7px;
	display: flex;
	justify-content: center;
	align-items: stretch;
	border-left: 1px solid var(--main-color-light);
	border-radius: 0px 5px 5px 0px;
	background-color: var(--main-color-2);
}

.de-input-search-options span {
	height: 100%;
	padding: 0px 4px;
	display: inline-flex;
	justify-content: center;
	align-items: center;
	color: var(--main-color-light);
	transition: background-color 0.2s ease-in-out;
}

.de-input-search-options span:last-child {
	text-decoration: underline;
}

.de-input-search-options span:hover {
	cursor: pointer;
	color: var(--main-color-dark) !important;
	background-color: var(--main-color-5);
}

.de-selected-search-option {
	color: var(--main-color-dark) !important;
	background-color: var(--main-color-5);
}

.de-search-bar button {
	width: 250px;
	flex: 1 1 250px;
	padding: 5px 10px;
	display: flex;
	justify-content: center;
	align-items: center;
	gap: 5px;
	font-size: 17px;
}

.de-loading-spinner {
	animation: spin 1.5s linear infinite;
}

.de-leaf-node {
	max-width: 200px;
	padding: 5px 10px;
	border: 2px solid var(--main-color-dark);
	border-radius: 5px;
	max-lines: 3;
	line-height: 14px;
	font-size: 16px;
	font-weight: bold;
	text-align: center;
	color: var(--main-color-dark);
	background-color: var(--main-color-leaf);
}

.de-wrap-searched-items-table,
.de-wrap-selected-items-table {
	width: 100%;
}

.de-searched-items-table,
.de-selected-items-table {
	width: 100%;
	padding: 2px;
	overflow: hidden;
	position: relative;
	box-sizing: border-box;
}

.de-wrap-button {
	width: 100%;
	margin: 10px 0px;
	text-align: center;
}

.de-wrap-button button {
	min-width: 200px;
	padding: 5px 10px;
	font-size: 18px;
}

.de-wrap-export-option {
	width: 50%;
	min-width: 300px;
	max-width: 500px;
	margin: 10px 0px;
}

.de-wrap-export-option label {
	margin: 0px 0px 5px 2px;
	display: block;
}

.de-wrap-export-option select,
.de-wrap-export-option input {
	width: 100%;
	padding: 5px 10px;
	font-size: 16px;
	background-color: var(--main-color-5);
	color: var(--main-color-dark);
}

.de-wrap-export-option input::placeholder {
	color: var(--main-color-dark);
}

.de-wrap-export-option select option {
	color: var(--main-color-dark);
}

.de-wrap-export-option input:valid,
.de-wrap-export-option select:valid {
	background-color: var(--main-color-2);
	color: var(--main-color-light);
}

.de-wrap-export-option select:valid option {
	color: var(--main-color-light);
}

.de-wrap-export-checkbox {
	margin: 15px 0px 0px 2px;
	display: flex;
	justify-content: flex-start;
	align-items: center;
	gap: 10px;
}

.de-wrap-export-checkbox label {
	cursor: pointer;
}
</style>
