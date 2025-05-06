<template>
	<div class="ou-wrap-content">
		<ConfirmationWindow v-if="confirmSubmission" :config="confirmSubmission" />
		<LoadingSpinner v-if="isUploading" :wrapperClass="'ou-wrap-content'" />
		<div class="ou-wrap-form">
			<StudyInfo :studyInfo="studyInfo" @newStudyInfo="setNewStudyInfo" />
		</div>
		<div class="ou-wrap-cu-btn">
			<button class="app-default-btn" @click="triggerFileUpload">{{ $t('ouUploadCodebook') }} <fai icon="fas fa-upload" /></button>
			<button :class="hasActiveCodebook ? 'app-default-btn' : 'app-disabled-btn'" @click="showMetaAssignment = true">
				{{ $t('ouMappCodebook') }} <fai icon="fas fa-sync" />
			</button>
		</div>
		<div v-if="showMetaAssignment" class="ou-wrap-meta-assignment" @click="showMetaAssignment = false">
			<MetaAssignment
				:codeBook="tableConfigsForCodeBooks[activeTab]"
				:metaAssignmentData="metaAssignmentData"
				@click.stop=""
				@close="showMetaAssignment = false"
				@updateMetaAssignment="saveMetaAssignments"
			/>
		</div>
		<input type="file" ref="fileInput" @change="uploadCodebookFile" accept=".csv" style="display: none" />
		<div class="ou-wrap-preview" v-if="tableConfigsForCodeBooks.length > 0">
			<div class="ou-tab-view">
				<div
					v-for="(tableConfig, index) in tableConfigsForCodeBooks"
					:key="tableConfig.name"
					:class="['ou-tab', { 'ou-current-tab': activeTab === index }]"
					@click="changeTab(index)"
					:title="tableConfig.name"
				>
					<span>{{ tableConfig.name.length > 17 ? tableConfig.name.substring(0, 17) + '...' : tableConfig.name }}</span>

					<fai icon="fas fa-times" @click.stop="deleteCodebook(index)" class="ou-close-icon" />
				</div>
			</div>
			<div class="ou-wrap-codebook-table">
				<LoadingSpinner v-if="isLoading" :wrapperClass="'ou-wrap-codebook-table'" />
				<Table
					v-if="tableConfigsForCodeBooks.length > 0"
					:key="tableConfigsForCodeBooks[activeTab].name"
					:config="tableConfigsForCodeBooks[activeTab].tableConfig"
					@selectItem="selectItem"
					@deleteRow="deleteRow"
					@deleteColumn="deleteColumn"
					@editHeader="editHeader"
					@updateRowOrder="updateRowOrder"
				/>
			</div>
			<div class="ou-wrap-assigned-items" v-if="selectedCbItem">
				<h2>{{ $t('ouManuellQuestItemInfo') }} {{ selectedCbItem.rowID }}</h2>
				<h3>{{ $t('ouTextInfo') }}</h3>
				<h3>{{ assignedItems.length ? $t('ouAssignableItems') : $t('ouNoItemsAvailable') }}</h3>

				<Table
					v-if="assignedItems.length > 0"
					:config="{
						...generateAssignedItemsTableConfig(assignedItems),
						selectedItemID: selectedAssignedItem,
					}"
					:startValue="selectedAssignedItem"
					:key="selectedAssignedItem"
					@selectItem="changeAssignedItemSelection"
				/>

				<div v-if="assignedItems.length > 0" class="ou-wrap-btn">
					<button class="app-warn-btn" @click="resetSelection">{{ $t('ceCancelSelection') }}</button>
					<button class="app-success-btn" @click="confirmSelection">{{ $t('ceConfirmSelection') }}</button>
				</div>
			</div>
			<div class="ou-wrap-su-btn">
				<button :class="isSubmitButtonEnabled ? 'app-success-btn' : 'app-disabled-btn'" @click="confirmStudySubmission">
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
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
import ConfirmationWindow from '@/components/general/ConfirmationWindow.vue';
import Table from '@/components/general/Table.vue';
import DataLoadWorker from '@/worker/codebookLoadWorker.js?worker';
import { codebookTableConfig } from '@/components/upload/codebookTableConfig';
import { linkedDataTableConfig } from '@/components/upload/linkedDataTableConfig';
import MetaAssignment from '@/components/upload/MetaAssignment.vue';
import metaData from '@/assets/dummy/metaData.json';

/**
 * @vuese
 * @group OntologyUpload
 * Provides the user with ontology upload functionality
 */
export default {
	name: 'OntologyUpload',
	components: { LoadingSpinner, StudyInfo, ConfirmationWindow, Table, MetaAssignment },
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
				drksId: null,
				description: null,
			},
			activeTab: 0,
			dummyOntologyDataStruct: dummyOntologyDataStruct,
			dataTableConfig: codebookTableConfig,
			tableConfigsForCodeBooks: [],
			linkedDataTableConfig: linkedDataTableConfig,
			selectedCbItem: null,
			assignedItems: null,
			selectedAssignedItem: null,
			selectedRow: null,
			linkedDataByTab: {},
			editingInProgress: false,
			confirmSubmission: null,
			metaData: metaData,
			metaAssignmentData: [],
			showMetaAssignment: false,
		};
	},
	computed: {
		allStudyInformationEntered() {
			let allStudyInformationValid = true;

			if (!this.studyInfo.name) allStudyInformationValid = false;
			else if (!this.studyInfo.purpose) allStudyInformationValid = false;
			else if (!this.studyInfo.dateStart) allStudyInformationValid = false;
			else if (!this.studyInfo.dateEnd) allStudyInformationValid = false;
			else if (!this.studyInfo.drksId) allStudyInformationValid = false;
			else if (!this.studyInfo.description) allStudyInformationValid = false;

			return allStudyInformationValid;
		},
		hasActiveCodebook() {
			const active = this.tableConfigsForCodeBooks[this.activeTab];
			return !!(active && active.tableConfig && active.tableConfig.data);
		},
		hasMetaAssignments() {
			let notFinishedYet = false;
			this.tableConfigsForCodeBooks.forEach((it) => {
				if (!it.metaAssignments || Object.keys(it.metaAssignments).length == 0) notFinishedYet = true;
			});
			return !notFinishedYet;
		},
		isSubmitButtonEnabled() {
			return this.allStudyInformationEntered && !this.editingInProgress && this.hasMetaAssignments;
		},
	},
	created() {
		this.queryMetaData();
	},
	methods: {
		queryMetaData() {
			this.$network.getData(`/api/ontology/meta?query_type=json`, null, null, (err, data) => {
				try {
					if (!err) this.metaAssignmentData = data.sort((a, b) => a.name.localeCompare(b.name));
					else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.isLoading = false;
					window.dispatchEvent(new Event('resize'));
				}
			});
		},
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
		saveMetaAssignments(assignments) {
			const codeBookMetaField = this.tableConfigsForCodeBooks[this.activeTab];
			codeBookMetaField.metaAssignments = assignments;

			this.uploadCodebook(codeBookMetaField);
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
								return {
									ref: [key],
									text: key,
									formatter: (cell) => {
										return this.$global.valueIsNotAvailable(cell, true) ? '-' : cell;
									},
								};
							});

							const newTableConfig = {
								name: fileName,
								tableConfig: {
									...this.dataTableConfig,
									data: { key: 'rowID', columns, values: data },
								},
							};

							this.tableConfigsForCodeBooks.push(newTableConfig);

							this.activeTab = this.tableConfigsForCodeBooks.length - 1;
						}
					};
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, error);
				}
			};
			reader.readAsText(file);
		},
		uploadCodebook(codebookConfig) {
			this.isLoading = true;

			const { tableConfig, metaAssignments } = codebookConfig;

			const codebook = {
				columns: tableConfig.data.columns.map((col) => (col.text === 'Zeile' ? 'rowID' : col.text)).filter((col) => col !== 'ouRowID'),
				rows: tableConfig.data.values.map((row) => {
					const { rowID, ...cells } = row;
					return {
						rowID,
						cells: [rowID, ...Object.values(cells).map((cell) => (cell === null || cell === undefined ? '' : String(cell)))],
					};
				}),
				metaAssignments,
			};

			this.$network.postData('/api/study/mapping', codebook, null, (err, data) => {
				try {
					if (!err) {
						this.processCodebookResponse(
							data.map((it) => {
								it.rowID = it.rowId;
								return it;
							})
						);
						this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('ouMappedMetaSuccess'));
					} else this.$global.showToast(TOAST_TYPE.ERROR, err.msg);
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.isLoading = false;
				}
			});
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
			}
		},
		getSelectedRow() {
			return this.tableConfigsForCodeBooks[this.activeTab].tableConfig.data.values.find((row) => row.rowID === this.selectedCbItem?.rowID);
		},
		selectItem(row) {
			const isSameRow = this.selectedCbItem?.rowID === row.rowID;
			this.selectedCbItem = isSameRow
				? null
				: this.tableConfigsForCodeBooks[this.activeTab].tableConfig.data.values.find((item) => item.rowID === row.rowID);

			this.assignedItems = this.selectedCbItem?.assignedItems || [];
			this.selectedAssignedItem = this.selectedCbItem?.assignedItemID || null;
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
				this.selectedCbItem = null;
				this.assignedItems = null;
				this.selectedAssignedItem = null;
				this.linkedDataTableConfig = null;

				this.activeTab = index;
			}
		},
		deleteCodebook(index) {
			this.tableConfigsForCodeBooks.splice(index, 1);

			this.activeTab = this.tableConfigsForCodeBooks.length > 0 ? Math.min(this.activeTab, this.tableConfigsForCodeBooks.length - 1) : -1;

			this.linkedDataTableConfig = null;
			this.selectedCbItem = null;
			this.assignedItems = null;
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
		editHeader({ ref, text }) {
			const trimmedText = text.trim();
			if (!trimmedText) {
				this.$global.showToast(TOAST_TYPE.WARN, this.$t('ouEmptyHeaderError'));
				return;
			}

			const selectedConfig = this.tableConfigsForCodeBooks[this.activeTab];
			const column = selectedConfig.tableConfig.data.columns.find((col) => col.ref.join('') === ref);

			if (column) {
				column.text = trimmedText;
			}
		},
		updateRowOrder(newOrder) {
			const selectedConfig = this.tableConfigsForCodeBooks[this.activeTab];
			selectedConfig.tableConfig.data.values = newOrder.map((row) => ({ ...row }));
		},
		changeAssignedItemSelection(updatedAssignedItem) {
			this.selectedAssignedItem = this.selectedAssignedItem === updatedAssignedItem.id ? null : updatedAssignedItem.id;
			this.pendingAssignedItem = this.selectedAssignedItem ? updatedAssignedItem : null;
		},
		confirmSelection() {
			if (!this.pendingAssignedItem || !this.selectedCbItem) return;

			const selectedRow = this.getSelectedRow();
			if (selectedRow) {
				const index = selectedRow.assignedItems.findIndex((item) => item.id === this.pendingAssignedItem.id);

				if (index !== -1) {
					selectedRow.assignedItems[index] = this.pendingAssignedItem;
				} else {
					selectedRow.assignedItems.push(this.pendingAssignedItem);
				}

				selectedRow.assignedItemID = this.pendingAssignedItem.id;
				this.selectedCbItem.assignedItemID = this.pendingAssignedItem.id;
				this.selectedAssignedItem = this.pendingAssignedItem.id;
				this.assignedItems = selectedRow.assignedItems;
				this.pendingAssignedItem = null;

				this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('ouConfirmItemSelection'));
			}
		},
		resetSelection() {
			if (!this.selectedCbItem) return;

			const selectedRow = this.getSelectedRow();
			if (selectedRow) {
				selectedRow.assignedItemID = null;
				this.selectedCbItem.assignedItemID = null;
				this.selectedAssignedItem = null;
				this.pendingAssignedItem = null;
				this.assignedItems = selectedRow.assignedItems;

				this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('ouConfirmItemRemove'));
			}
		},
		submitStudy() {
			this.isUploading = true;

			let codebooks = [];

			this.tableConfigsForCodeBooks.forEach((it) => {
				codebooks.push({
					name: it.name,
					columns: it.tableConfig.data.columns
						.filter((col) => !['assignedItemID', 'assignedItems', 'rowID'].includes(col.ref.join('')))
						.map((col, idx) => {
							return {
								header: col.text,
								assignedMetaTag: it.metaAssignments.find((meta) => meta.id == idx)?.metaDataItemTag || null,
							};
						}),
					rows: it.tableConfig.data.values.map((row) => {
						const { rowID, assignedItems, assignedItemID, ...cells } = row;
						return {
							cells: Object.values(cells).map((cell) => (cell === null || cell === undefined ? '' : String(cell))),
							rowID,
							assignedItemID,
						};
					}),
				});
			});

			const studySubmission = {
				studyInfo: this.studyInfo,
				codebooks: codebooks,
			};

			this.$network.postData('/api/study/', studySubmission, null, (err, data) => {
				try {
					if (!err) {
						this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('ctStudySubmission'));
						this.$router.push({ name: ROUTE.PROFILE });
					} else this.$global.showToast(TOAST_TYPE.ERROR, err.msg);
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.isUploading = false;
				}
			});
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
	display: flex;
	flex-direction: row;
	gap: 15px;
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

.ou-wrap-codebook-table,
.ou-wrap-assigned-items {
	position: relative;
	overflow: hidden;
	padding: 0px 2px 2px 2px;
}

.ou-tab-view {
	width: 100%;
	margin: 10px 0px 0px 0px;
	display: flex;
	justify-content: flex-start;
	align-items: flex-start;
	gap: 5px;
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
	position: relative;
}

.ou-tab span {
	display: block;
	max-width: 100%;
	width: 100%;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	color: var(--main-color-dark);
}

.ou-tab .ou-close-icon {
	position: absolute;
	top: 5px;
	right: 5px;
	cursor: pointer;
	font-size: 16px;
}

.ou-tab svg * {
	color: var(--main-color-dark);
}

.ou-close-icon:hover * {
	color: var(--main-color-error);
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
.ou-wrap-btn {
	width: 100%;
	text-align: center;
	display: flex;
	justify-content: flex-end;
	margin-top: 15px;
}

.ou-wrap-btn button {
	min-width: 200px;
	height: 40px;
	margin: 5px;
	font-size: 16px;
}

.ou-wrap-meta-assignment {
	width: 100%;
	height: 100%;
	padding: 10px 30px;
	position: fixed;
	top: 0px;
	left: 0px;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: row;
	z-index: 2;
	box-sizing: border-box;
	background-color: var(--main-color-dark-80);
}
</style>
