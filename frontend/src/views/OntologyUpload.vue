<template>
	<div class="ou-wrap-content">
		<ConfirmationWindow v-if="confirmSubmission" :config="confirmSubmission" />
		<LoadingSpinner v-if="isUploading" :wrapperClass="'ou-wrap-content'" />
		<div class="ou-wrap-form">
			<StudyInfo :studyInfo="studyInfo" @newStudyInfo="setNewStudyInfo" />
		</div>
		<div class="ou-wrap-cu-btn">
			<button class="app-default-btn" @click="triggerFileUpload">{{ $t('ouUploadCodebook') }} <fai icon="fas fa-upload" /></button>
		</div>
		<input type="file" ref="fileInput" @change="uploadCodebookFile" accept=".csv" style="display: none" />
		<div class="ou-wrap-preview" v-if="tableConfigsForCodeBooks.length > 0">
			<div class="ou-tab-view">
				<div
					v-for="(tableConfig, index) in tableConfigsForCodeBooks"
					:key="tableConfig.name"
					:class="['ou-tab', { 'ou-current-tab': activeTab === index }]"
					@click="changeTab(index)"
				>
					{{ tableConfig.name }}

					<fai icon="fas fa-times" @click.stop="deleteCodebook(index)" />
				</div>
			</div>
			<div class="ou-wrap-codebook-table">
				<LoadingSpinner v-if="isLoading" :wrapperClass="'ou-wrap-codebook-table'" />
				<Table
					v-if="tableConfigsForCodeBooks.length > 0"
					:key="activeTab"
					:config="tableConfigsForCodeBooks[activeTab].tableConfig"
					@selectItem="selectItem"
					@deleteRow="deleteRow"
					@deleteColumn="deleteColumn"
				/>
			</div>
			<div class="ou-wrap-assigned-items" v-if="selectedCbItem">
				<h2>{{ $t('ouManuellQuestItemInfo') }} {{ selectedCbItem.rowID }}</h2>
				<h3>{{ $t('ouTextInfo') }}</h3>
				<h3>{{ selectedAssignedItems.length ? $t('ouAssignableItems') : $t('ouNoItemsAvailable') }}</h3>

				<Table v-if="selectedAssignedItems.length" :config="generateAssignedItemsTableConfig(selectedAssignedItems)" />
			</div>
			<div class="ou-wrap-su-btn">
				<button
					:class="allStudyInformationEntered && !editingInProgress ? 'app-success-btn' : 'app-disabled-btn'"
					@click="confirmStudySubmission"
				>
					{{ $t('ouSubmitStudy') }} <fai icon="fas fa-paper-plane" />
				</button>
			</div>
		</div>
	</div>
</template>

<script>
import { TOAST_TYPE, ROUTE } from '@/enums/enums';
import dummyOntologyDataStruct from '@/assets/dummy/dummyOntologyDataStruct.json';
import StudyInfo from '@/components/upload/StudyInfo.vue';
import CodebookTable from '@/components/upload/CodebookTable.vue';
import CodebookElement from '@/components/upload/CodebookElement.vue';
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
import ConfirmationWindow from '@/components/general/ConfirmationWindow.vue';
import Table from '@/components/general/Table.vue';
import DataLoadWorker from '@/worker/codebookLoadWorker.js?worker';
import { codebookTableConfig } from '@/components/upload/codebookTableConfig';
import { linkedDataTableConfig } from '@/components/upload/linkedDataTableConfig';

/**
 * @vuese
 * @group OntologyUpload
 * Provides the user with ontology upload functionality
 */
export default {
	name: 'OntologyUpload',
	components: { CodebookTable, CodebookElement, LoadingSpinner, StudyInfo, ConfirmationWindow, Table },
	setup() {
		return { ROUTE };
	},
	data() {
		return {
			isLoading: false,
			isUploading: false,
			studyInfo: {
				name: null,
				purpose: null,
				dateStart: null,
				dateEnd: null,
				drksID: null,
				description: null,
			},
			activeTab: 0,
			dummyOntologyDataStruct: dummyOntologyDataStruct,
			dataTableConfig: codebookTableConfig,
			tableConfigsForCodeBooks: [],
			linkedDataTableConfig: linkedDataTableConfig,
			selectedCbItem: null,
			selectedAssignedItems: null,
			selectedAssignedItem: null,

			tables: [],
			selectedRow: null,
			linkedDataByTab: {},
			editingInProgress: false,
			confirmSubmission: null,
		};
	},
	computed: {
		allStudyInformationEntered() {
			let allStudyInformationValid = true;

			if (!this.studyInfo.name) allStudyInformationValid = false;
			else if (!this.studyInfo.purpose) allStudyInformationValid = false;
			else if (!this.studyInfo.dateStart) allStudyInformationValid = false;
			else if (!this.studyInfo.dateEnd) allStudyInformationValid = false;
			else if (!this.drksIdIsValid(this.studyInfo.drksID)) allStudyInformationValid = false;
			else if (!this.studyInfo.description) allStudyInformationValid = false;

			return allStudyInformationValid;
		},
	},
	methods: {
		setNewStudyInfo(info) {
			this.studyInfo = info;

			if (
				this.studyInfo.dateStart &&
				!this.studyInfo.dateStart.startsWith('0') &&
				this.studyInfo.dateEnd &&
				!this.studyInfo.dateEnd.startsWith('0') &&
				!this.datesValid(this.studyInfo.dateStart, this.studyInfo.dateEnd)
			) {
				this.$global.showToast(TOAST_TYPE.WARN, this.$t('ouInvalidDateRange'));
			}

			if (this.studyInfo.drksID && !this.drksIdIsValid(this.studyInfo.drksID))
				this.$global.showToast(TOAST_TYPE.WARN, this.$t('ouInvalidDrksId'));
		},
		datesValid(dateStart, dateEnd) {
			if (dateStart && dateEnd) {
				return new Date(dateStart) < new Date(dateEnd);
			}
			return true;
		},
		drksIdIsValid(value) {
			const numericPattern = /^\d+$/;
			return numericPattern.test(value);
		},
		triggerFileUpload() {
			this.$refs.fileInput.click();
		},
		uploadCodebookFile(event) {
			const file = event.target.files[0];
			event.target.value = '';
			if (!file) return;

			// Remove the file extension from fileName
			const fileName = file.name.replace(/\.[^/.]+$/, '');

			// Check whether a table with the same file name has already been uploaded
			if (this.tableConfigsForCodeBooks.some((config) => config.name === fileName)) {
				this.$global.showToast(TOAST_TYPE.WARN, this.$t('ctDataAlreadyUploaded'));
				return;
			}

			const reader = new FileReader();
			reader.onload = async (e) => {
				try {
					const fileData = e.target.result;

					const worker = new DataLoadWorker();

					worker.postMessage({ fileData });

					worker.onmessage = (e) => {
						const { type, data } = e.data;
						if (type == 'TOAST') that.$global.showToast(TOAST_TYPE.ERROR, that.$t(data));
						else if (type === 'RESULT') {
							const columns = Object.keys(data[0]).map((key) => {
								if (key === 'rowID') {
									return { ref: ['rowID'], text: this.$t('ouRowID'), ignoreFunctions: true };
								}
								return { ref: [key], text: key };
							});

							const rows = data.map((row) => {
								let newRow = { ...row };
								Object.keys(newRow).forEach((key) => {
									if (!newRow[key] || newRow[key] === '') {
										newRow[key] = '-';
									}
								});
								return newRow;
							});

							const newTableConfig = {
								name: fileName,
								tableConfig: {
									...this.dataTableConfig,
									data: { key: 'rowID', columns, values: rows },
								},
							};

							this.uploadCodebook({ columns, rows });

							this.tableConfigsForCodeBooks.push(newTableConfig);

							this.activeTab = this.tableConfigsForCodeBooks.length - 1;

							//console.log('Neue Tabellenkonfiguration:', JSON.stringify(newTableConfig));

							/*const filteredRows = this.tableConfigsForCodeBooks.flatMap((config) =>
							config.tableConfig.data.values.filter((row) => row.rowID === 2)
							console.log('Alle Zeilen mit rowID === 2:', JSON.stringify(filteredRows));*/
						}
					};
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, error);
				}
			};
			reader.readAsText(file);
		},
		uploadCodebook(data) {
			this.isLoading = true;

			const codebook = {
				columns: data.columns.filter((col) => col.text !== 'ouRowID').map((col) => col.text),
				rows: data.rows.map((row) => ({
					rowID: row.rowID,
					cells: Object.values(row)
						.filter((_, i) => i !== 0)
						.map(String),
				})),
			};

			let codebookJson = JSON.stringify(codebook);
			//console.log(codebookJson);

			window.setTimeout(() => {
				this.$network.postData('/api/codebook/mapping', codebookJson, null, (err, data) => {
					try {
						// TODO: Remove mocked data and timeout
						/*if (!err) {
							this.processCodebookResponse(data);
							this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('ctFileUploaded'));
						}*/
						if (err) {
							this.processCodebookResponse(this.dummyOntologyDataStruct);
							this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('ctFileUploaded'));
						} else this.$global.showToast(TOAST_TYPE.ERROR, err.msg);
					} catch (error) {
						this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
					} finally {
						this.isLoading = false;
					}
				});
			}, 2000);
		},
		processCodebookResponse(response) {
			this.linkedDataByTab[this.activeTab] = response;

			const tableConfig = this.tableConfigsForCodeBooks[this.activeTab];
			if (tableConfig) {
				const assignedItemsMap = new Map(response.map((item) => [item.rowID, item.assignedItems || []]));

				const updatedRows = tableConfig.tableConfig.data.values.map((row) => {
					const assignedItems = assignedItemsMap.get(row.rowID) || [];
					row.assignedItems = assignedItems;

					// Mapp the ID of the first assignedItem, if available
					if (assignedItems.length > 0) {
						row.assignedItemID = assignedItems[0].id;
					} else {
						row.assignedItemID = null;
					}

					return row;
				});

				tableConfig.tableConfig.data.values = updatedRows;

				//const rowWithId2 = updatedRows.find((row) => row.rowID === 3);
				//rowWithId2 && console.log('Erste Zeile mit rowID === 3:', JSON.stringify(rowWithId2, null, 2));
			}
		},
		selectItem(row) {
			// Holt das ausgewählte `selectedCbItem` aus der Haupttabelle
			this.selectedCbItem = this.tableConfigsForCodeBooks[this.activeTab].tableConfig.data.values.find((item) => item.rowID === row.rowID);

			// Setzt die `assignedAssignedItems` für die angezeigte Zeile
			this.selectedAssignedItems = this.selectedCbItem ? this.selectedCbItem.assignedItems : [];

			// Setzt die `assignedItemID` direkt aus dem ausgewählten `selectedCbItem`
			this.selectedAssignedItem = this.selectedCbItem?.assignedItemID || null;

			console.log('selectedAssignedItem:', this.selectedAssignedItem);
		},
		generateAssignedItemsTableConfig(assignedItems) {
			return {
				...this.linkedDataTableConfig,
				data: {
					key: 'id',
					columns: assignedItems[0]
						? Object.keys(assignedItems[0]).map((key) => ({
								ref: [key],
								text: key === 'id' ? this.$t('ouItemID') : key,
							}))
						: [],
					values: assignedItems,
				},
			};
		},
		changeTab(index) {
			if (index !== this.activeTab) {
				this.activeTab = index;
			}
		},
		deleteCodebook(index) {
			this.tableConfigsForCodeBooks.splice(index, 1);

			this.activeTab = this.tableConfigsForCodeBooks.length > 0 ? Math.min(this.activeTab, this.tableConfigsForCodeBooks.length - 1) : -1;

			this.linkedDataTableConfig = null;
			this.selectedCbItem = null;
			this.selectedAssignedItems = null;

			/*console.log(
				'Verbleibende Codebooks:',
				this.tableConfigsForCodeBooks.map((config) => config.name)
			);
			console.log('linkedDataTableConfig nach dem Löschen:', JSON.stringify(this.linkedDataTableConfig));*/
		},
		deleteRow(row) {
			const selectedConfig = this.tableConfigsForCodeBooks[this.activeTab];
			selectedConfig.tableConfig.data.values = selectedConfig.tableConfig.data.values.filter(
				(value) => value[selectedConfig.tableConfig.data.key] !== row[selectedConfig.tableConfig.data.key]
			);
		},
		deleteColumn(columnKey) {
			const selectedConfig = this.tableConfigsForCodeBooks[this.activeTab];
			const cleanColumnKey = Array.isArray(columnKey) ? columnKey[0] : columnKey;

			if (selectedConfig.tableConfig.data.columns.some((col) => col.ref[0] === cleanColumnKey)) {
				selectedConfig.tableConfig.data.columns = selectedConfig.tableConfig.data.columns.filter((col) => col.ref[0] !== cleanColumnKey);
				selectedConfig.tableConfig.data.values = selectedConfig.tableConfig.data.values.map(({ [cleanColumnKey]: _, ...row }) => row);
			}
		},
		submitStudy() {
			this.isUploading = true;

			const studySubmission = {
				studyInfo: { ...this.studyInfo },
				codeBooks: this.tableConfigsForCodeBooks.map(({ name, tableConfig }) => ({
					name,
					columns: tableConfig.data.values[0]
						? Object.keys(tableConfig.data.values[0]).filter((col) => !['assignedItemID', 'assignedItems', 'rowID'].includes(col))
						: [],
					rows: tableConfig.data.values.map((row) => {
						const { rowID, assignedItems, assignedItemID, ...cells } = row;
						return {
							cells: Object.values(cells),
							assignedItemID,
						};
					}),
				})),
			};

			const studySubmissionJson = JSON.stringify(studySubmission);
			//console.log('studySubmissionJson:', JSON.stringify(studySubmission, null, 2));

			window.setTimeout(() => {
				this.$network.postData('/api/codebooks/submit-study', studySubmissionJson, null, (err, data) => {
					try {
						// TODO: Remove timeout
						// if (!err)
						if (err) {
							this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('ctStudySubmission'));
							this.$router.push({ name: ROUTE.PROFILE });
						} else this.$global.showToast(TOAST_TYPE.ERROR, err.msg);
					} catch (error) {
						this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
					} finally {
						this.isUploading = false;
					}
				});
			}, 2000);
		},
		confirmStudySubmission() {
			this.confirmSubmission = {
				title: this.$t('ceConfirmStudySubmissionTitel'),
				text: this.$t('ceConfirmStudySubmissionText'),
				cancelButton: {
					class: 'app-default-btn',
					text: this.$t('ceCancel'),
					callback: () => {
						this.isLoading = false;
						this.confirmSubmission = null;
					},
				},
				confirmButton: {
					class: 'app-warn-btn',
					text: this.$t('ceConfirmStudySubmission'),
					callback: () => {
						this.confirmSubmission = null;
						this.submitStudy();
					},
				},
			};
		},

		//AB HIER ALT
		setSelectedRow(row) {
			this.selectedRow = row;
		},
		updateTableRows({ activeTab, deletedLineNumber }) {
			const linkedData = this.linkedDataByTab[activeTab];
			const linkedDataIndex = linkedData.findIndex((data) => data.lineNumber === deletedLineNumber);

			// Delete linkedData
			if (linkedDataIndex !== -1) {
				linkedData.splice(linkedDataIndex, 1);
			}

			this.linkedDataByTab[activeTab] = [...linkedData];

			this.tables = this.tables.map((table) => {
				if (table.tabIndex === activeTab) {
					table.tableData = table.tableData.filter((row) => row['#'] !== deletedLineNumber);
				}
				return table;
			});
		},
		updateTables(updatedTables) {
			this.tables = updatedTables;
		},
		updateLinkedData(index) {
			const updatedLinkedData = {};
			for (const [key, value] of Object.entries(this.linkedDataByTab)) {
				const newKey = key > index ? key - 1 : key;
				if (newKey >= 0) {
					updatedLinkedData[newKey] = value;
				}
			}
			this.linkedDataByTab = updatedLinkedData;
		},
		updateAssignedItem(updatedRow) {
			const rowIndex = this.tables[this.activeTab].rows.findIndex((row) => row.lineNumber === updatedRow.lineNumber);

			if (rowIndex !== -1) {
				this.tables[this.activeTab].rows[rowIndex].assignedItemID = updatedRow.assignedItemID;
			}

			this.linkedDataByTab[this.activeTab] = this.linkedDataByTab[this.activeTab].map((item) => {
				if (item.lineNumber === updatedRow.lineNumber) {
					return { ...item, assignedItemID: updatedRow.assignedItemID };
				}
				return item;
			});

			this.$forceUpdate();
		},
		setEditingStatus(status) {
			this.editingInProgress = status;
		},
	},
};
</script>

<style scoped>
.ou-wrap-content {
	width: 100%;
	position: relative;
	overflow: hidden;
}

.ou-wrap-form {
	display: flex;
	justify-content: flex-start;
	align-items: flex-start;
	flex-flow: wrap;
}

.ou-inputs-left {
	flex: 1;
}

.ou-wrap-textarea {
	justify-content: flex-start;
	align-items: flex-start;
	flex-flow: wrap;
}

.ou-inputs-row {
	display: flex;
	justify-content: flex-start;
	align-items: flex-start;
	flex-flow: wrap;
}

.ou-wrap-cu-btn {
	width: 100%;
	margin: 5px;
}

.ou-wrap-su-btn {
	width: 100%;
	margin: 5px;
	text-align: center;
}

.ou-wrap-cu-btn button,
.ou-wrap-su-btn button {
	margin: 10px 0 20px 0;
	padding: 10px 20px;
	font-size: 18px;
}

.ou-wrap-codebook-table {
	position: relative;
	overflow: hidden;
}

.ou-wrap-assigned-items {
	position: relative;
	overflow: hidden;
}

.ou-tab-view {
	width: 100%;
	margin: 10px 0px 0px 0px;
	display: flex;
	justify-content: flex-start;
	align-items: flex-start;
	gap: 5px;
	padding-bottom: 2px;
}

.ou-tab {
	width: 200px;
	padding: 5px 10px;
	border: 2px solid var(--main-color-dark);
	border-bottom: 2px solid var(--main-color-light);
	border-radius: 10px 10px 0px 0px;
	text-align: center;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
	background-color: var(--main-color-4);
	color: var(--main-color-dark);
}

.ou-tab:hover {
	cursor: pointer;
	background-color: var(--main-color-5);
}

.ou-current-tab {
	background-color: var(--main-color-5);
}

.ou-wrap-assigned-items h2 {
	margin: 20px 0 10px 0;
	padding: 1px;
	font-weight: normal;
}

.ou-wrap-assigned-items h3 {
	margin: 20px 0 5px 0;
	padding: 1px;
	font-weight: normal;
	text-align: justify;
	word-wrap: break-word;
}
</style>
