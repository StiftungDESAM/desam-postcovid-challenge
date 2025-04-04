<template>
	<div class="du-wrap-content">
		<LoadingSpinner v-if="isUploading" :wrapperClass="'du-wrap-content'" />
		<div class="du-wrap-studies-table">
			<LoadingSpinner v-if="isLoading" :wrapperClass="'du-wrap-studies-table'" />
			<Table :config="studyTableConfig" @selectItem="selectStudy" />
		</div>
		<div v-if="selectedStudy" class="du-wrap-selected-study">
			<div class="du-wrap-upload">
				<button class="app-default-btn" @click="$refs.fileInput.click()">{{ $t('duUploadData') }} <fai icon="fas fa-upload" /></button>
				<input type="file" ref="fileInput" @change="uploadFile" :accept="['.csv']" style="display: none" />
			</div>

			<div class="du-wrap-row-mapping">
				<div class="du-wrap-mapping">
					<label>{{ $t('duColumnIdentifier') }}</label>
					<select v-model="mappingColumn" @change="changeMapping" disabled>
						<!-- <option :value="null" default selected hidden>{{ $t('duSelectMapping') }}</option> -->
						<!-- <option :value="null" default selected>{{ $t('duDeselectMapping') }}</option> -->
						<option v-for="col in currentColumnMapping?.mappings" :key="col.id" :value="col.id">
							{{ col.assignedItem ? col.assignedItem : col.name }}
						</option>
					</select>
				</div>
				<div class="du-wrap-mapping">
					<label>{{ $t('duColumnTranslation') }}</label>
					<select v-model="translationColumn" @change="changeTranslation">
						<option :value="null" default selected hidden>{{ $t('duSelectTranslation') }}</option>
						<option :value="null" default selected>{{ $t('duDeselectTranslation') }}</option>
						<option v-for="col in currentColumnMapping?.data" :key="col.id" :value="col.id">
							{{ col.assignedItem ? col.assignedItem : col.name }}
						</option>
					</select>
				</div>
				<div v-if="selectedCodeBook" class="du-wrap-quality-check-button">
					<button class="app-default-btn" @click="showDataQualityCheck = true">
						{{ $t('duCheckDataQuality') }} <fai icon="fa-solid fa-magnifying-glass-chart" />
					</button>
				</div>
			</div>
			<div v-if="showDataQualityCheck" class="du-wrap-data-quality-check" @click="showDataQualityCheck = false">
				<DataQualityCheck
					:codeBook="selectedCodeBook"
					:mode="dqcmEnum.UPLOAD"
					@click.stop=""
					@close="showDataQualityCheck = false"
					@setConfig="setDataQualityCheckConfig"
					@checkResult="setDataQualityCheckResult"
				/>
			</div>
			<div class="du-wrap-data-table">
				<div class="du-tab-view">
					<div
						v-for="codeBook in selectedStudy.codeBooks"
						:key="codeBook.id"
						:class="['du-tab', codeBook.id == selectedCodeBook.id ? 'du-current-tab' : '']"
						@click="selectCodeBook(codeBook.id)"
					>
						{{ codeBook.name }}
					</div>
				</div>
				<div v-for="config in tableConfigsForCodeBooks" :key="config.id" class="du-data-table">
					<Table
						v-if="config.id == selectedCodeBook.id && config.tableConfig"
						:config="config.tableConfig"
						@selectItem="selectItem"
						@deleteRow="deleteRow"
						@clickedErrorIcon="clickedErrorIcon"
						@clickedWarningIcon="clickedWarningIcon"
					/>
					<div
						v-if="config.id == selectedCodeBook.id && config.tableConfig && detailedInfo"
						class="du-wrap-detailed-info"
						@click="detailedInfo = null"
					>
						<div @click.stop class="du-detailed-info">
							<fai v-if="detailedInfo.type == 'ERROR'" icon="fas fa-circle-xmark" class="du-error-svg" />
							<fai v-else-if="detailedInfo.type == 'WARNING'" icon="fas fa-triangle-exclamation" class="du-warning-svg" />
							<div v-for="(info, idx) in detailedInfo.values" :key="idx">
								<p>
									<strong>{{ $t('duRow') }}:</strong> {{ info.rowRef || '-' }}
								</p>
								<p>
									<strong>{{ $t('duColumn') }}:</strong> {{ info.colRef || '-' }}
								</p>
								<p>
									<strong>{{ $t('duMessage') }}:</strong> {{ $t(info.text) }}
								</p>
							</div>
						</div>
					</div>
				</div>
			</div>
			<AssignedAndLinkedData
				v-if="selectedItem"
				:linkedItem="linkedItem"
				:mappedItems="mappedItems"
				:mappingColumn="selectedCodeBook?.data[mappingColumn]"
			/>
			<div class="du-wrap-bottom">
				<div class="du-wrap-data-status">
					<p v-if="!checkResultOfData.allChecksPerformed">
						<fai icon="fas fa-circle-info" class="du-info-svg" /> {{ $t('duCheckOfDataMissing') }}
					</p>
					<p v-else-if="checkResultOfData.errors > 0">
						<fai icon="fas fa-circle-xmark" class="du-error-svg" /> {{ $t('duErrorsInDataExist') }}
					</p>
					<p v-else-if="checkResultOfData.warnings > 0">
						<fai icon="fas fa-triangle-exclamation" class="du-warning-svg" />{{ $t('duWarningsInDataExist') }}
					</p>
					<p v-else><fai icon="fas fa-circle-check" class="du-success-svg" />{{ $t('duDataCanBeUploaded') }}</p>
				</div>
				<div class="du-wrap-buttons">
					<button :class="uploadAllowed ? 'app-success-btn' : 'app-disabled-btn'" @click="uploadData">
						{{ $t('duSubmitData') }} <fai icon="fas fa-paper-plane" />
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import Table from '@/components/general/Table.vue';
import DataLoadWorker from '@/worker/dataLoadWorker.js?worker';
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
import { studyTableConfig } from '@/components/upload/studyTableConfig';
import { dataTableConfig } from '@/components/upload/dataTableConfig';
import studies from '@/assets/dummy/studies.json';
import detailedStudy from '@/assets/dummy/detailedStudy.json';
import { ROUTE, TOAST_TYPE, DATA_QUALITY_CHECK_MODE } from '@/enums/enums';
import AssignedAndLinkedData from '@/components/upload/AssignedAndLinkedData.vue';
import DataQualityCheck from '@/components/upload/DataQualityCheck.vue';
import { reactive } from 'vue';
/**
 * @vuese
 * @group DataUpload
 * Provides the user with data upload functionality
 */
export default {
	name: 'DataUpload',
	components: { Table, LoadingSpinner, AssignedAndLinkedData, DataQualityCheck },
	emits: [],
	props: {},
	watch: {},
	setup() {
		const dqcmEnum = DATA_QUALITY_CHECK_MODE;
		return { dqcmEnum };
	},
	data() {
		return {
			isLoading: false,
			isUploading: false,
			studies: studies,
			study: detailedStudy,
			studyTableConfig: studyTableConfig,
			dataTableConfig: dataTableConfig,
			selectedStudy: null,
			showDataQualityCheck: false,
			selectedCodeBook: null,
			tableConfigsForCodeBooks: [],
			mappingColumn: null,
			translationColumn: null,
			selectedItem: null,
			assignedMetaItem: null,
			detailedInfo: null,
		};
	},
	computed: {
		currentColumnMapping() {
			return this.tableConfigsForCodeBooks.find((it) => it.id == this.selectedCodeBook.id);
		},
		mappedItems() {
			const mappedItems = [];
			let idx = this.selectedCodeBook?.data[this.mappingColumn].rows.findIndex((d) => d == this.selectedItem?.ref.join(''));

			this.selectedCodeBook?.data.forEach((it) => {
				mappedItems.push({
					name: it.name,
					value: it.rows[idx],
					assignedMetaField: it.assignedMetaField,
				});
			});

			return mappedItems;
		},
		linkedItem() {
			let idx = this.selectedCodeBook?.data[this.mappingColumn].rows.findIndex((d) => d == this.selectedItem?.ref.join(''));

			return this.selectedCodeBook?.linkedData[idx];
		},
		checkResultOfData() {
			const checkResults = {
				allChecksPerformed: true,
				errors: 0,
				warnings: 0,
			};

			this.tableConfigsForCodeBooks.forEach((codeBook) => {
				if (codeBook.dataQualityCheckConfig?.result) {
					checkResults.errors += codeBook.dataQualityCheckConfig.result.errors.length;
					checkResults.warnings += codeBook.dataQualityCheckConfig.result.warnings.length;
				} else checkResults.allChecksPerformed = false;
			});

			return checkResults;
		},
		uploadAllowed() {
			return this.checkResultOfData.allChecksPerformed && this.checkResultOfData.errors == 0;
		},
	},
	created() {
		this.queryStudies();
	},
	mounted() {},
	beforeDestroy() {},
	methods: {
		queryStudies() {
			this.isLoading = true;

			this.$network.getData(`/api/data/studies`, null, null, (err, data) => {
				try {
					// TODO: Remove mocked data
					// if (!err) this.tableConfig.data.values = data;
					if (err) this.studyTableConfig.data.values = this.studies;
					else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.isLoading = false;
					window.dispatchEvent(new Event('resize'));
				}
			});
		},
		selectStudy(study) {
			this.resetView();
			if (study) {
				this.isLoading = true;

				this.$network.getData(`/api/data/studies/${study.id}`, null, null, (err, data) => {
					try {
						// TODO: Remove mocked data
						// if (!err) this.selectedStudy = data;
						if (err) {
							this.selectedStudy = this.study;
							this.mappingColumn = this.selectedStudy.codeBooks[0].mappingColumn;
							this.translationColumn = this.selectedStudy.codeBooks[0].translationColumn;

							this.selectedStudy.codeBooks.forEach((codeBook) => {
								this.tableConfigsForCodeBooks.push({
									id: codeBook.id,
									name: codeBook.name,
									tableConfig: null,
									mappings: codeBook.data.filter((it) => new Set(it.rows).size == it.rows.length),
									data: codeBook.data,
									linkedData: codeBook.linkedData,
									dataQualityCheckConfig: null,
								});
							});
							this.selectedCodeBook = this.tableConfigsForCodeBooks.find((it) => it.id == this.selectedStudy.codeBooks[0].id);
						} else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
					} catch (error) {
						this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
					} finally {
						this.isLoading = false;
						window.dispatchEvent(new Event('resize'));
					}
				});
			}
		},
		uploadFile(e) {
			this.isUploading = true;
			const file = e.target.files[0];
			e.target.value = '';
			if (!file) return;

			const reader = new FileReader();
			reader.onload = async (e) => {
				try {
					const worker = new DataLoadWorker();

					// TODO: Find better more reactive solution. Maybe remove worker again because the load isnt that big
					let that = this;
					worker.onmessage = (e) => {
						that.isUploading = false;
						if (e.data.type == 'TOAST') that.$global.showToast(TOAST_TYPE.ERROR, that.$t(e.data.data));
						else if (e.data.type == 'RESULT') {
							that.dataTableConfig.data.columns = [];
							that.dataTableConfig.data.values = [];
							let configs = [];
							e.data.data.forEach((it) => {
								it.tableConfig?.data?.columns?.map((col) => {
									if (col.formatter) {
										col.formatter = (value) => {
											return !value || value == '' ? '-' : value;
										};
									}

									return col;
								});
								configs.push(it);
							});

							that.tableConfigsForCodeBooks = configs;
							that.selectedCodeBook = configs.find((it) => it.id == that.selectedCodeBook.id);
						}
					};

					const mappedTableConfigsForCodeBooks = [];
					this.tableConfigsForCodeBooks.forEach((it) => {
						it.tableConfig?.data?.columns?.map((col) => {
							if (col.formatter) col.formatter = true;

							return col;
						});
						mappedTableConfigsForCodeBooks.push(it);
					});

					worker.postMessage(
						JSON.parse(
							JSON.stringify({
								fileData: e.target.result.toString(),
								dataTableConfig: this.dataTableConfig,
								tableConfigsForCodeBooks: mappedTableConfigsForCodeBooks,
								selectedCodeBook: this.selectedCodeBook,
								translationColumn: this.translationColumn,
								mappingColumn: this.mappingColumn,
							})
						)
					);

					this.selectedItem = null;
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, error);
				}
			};

			reader.readAsText(file);
		},
		selectCodeBook(id) {
			this.selectedCodeBook = this.tableConfigsForCodeBooks.find((it) => it.id == id);
			this.mappingColumn = this.selectedStudy.codeBooks.find((it) => it.id == id).mappingColumn;
			this.translationColumn = this.selectedStudy.codeBooks.find((it) => it.id == id).translationColumn;
			this.selectedItem = null;
			this.assignedMetaItem = null;
		},
		changeMapping() {
			// TODO: Check if this should even be allowed
		},
		changeTranslation() {
			this.selectedStudy.codeBooks.map((it) => {
				if (it.id == this.selectedCodeBook.id) it.translationColumn = this.translationColumn;
				return it;
			});

			const translationRegex = new RegExp(/\(.*\)/);
			this.tableConfigsForCodeBooks.map((tc) => {
				if (tc.id == this.selectedCodeBook.id) {
					tc.tableConfig.data.columns.map((it, idx) => {
						if (idx != 0) {
							if (translationRegex.test(it.text))
								it.text = it.text.replace(
									translationRegex,
									this.translationColumn != null ? `(${this.getTranslationForColumn(it.ref[0])})` : ''
								);
							else it.text = `${it.text} ${this.translationColumn != null ? `(${this.getTranslationForColumn(it.ref[0])})` : ''}`;
						}
						return it;
					});
				}
				return tc;
			});
		},
		getIdxOfColumn(ref) {
			const columnMapping = this.tableConfigsForCodeBooks.find((codeBook) => codeBook.id == this.selectedCodeBook.id);
			const mappingColumn = columnMapping.mappings.find((it) => it.id == this.mappingColumn);
			return mappingColumn.rows.findIndex((it) => it == ref);
		},
		getTranslationForColumn(ref) {
			if (this.translationColumn) {
				const refIdx = this.getIdxOfColumn(ref);
				const columnMapping = this.tableConfigsForCodeBooks.find((codeBook) => codeBook.id == this.selectedCodeBook.id);
				const translationColumn = columnMapping.data.find((it) => it.id == this.translationColumn);
				return refIdx >= 0 ? translationColumn.rows[refIdx] : '-';
			} else return '-';
		},
		selectItem(item) {
			this.selectedItem = item;
		},
		deleteRow(row) {
			this.tableConfigsForCodeBooks.map((it) => {
				if (it.id == this.selectedCodeBook.id)
					it.tableConfig.data.values = it.tableConfig.data.values.filter(
						(value) => value[it.tableConfig.data.key] != row[it.tableConfig.data.key]
					);

				return it;
			});
		},
		setDataQualityCheckConfig(config) {
			let updatedConfig = null;
			this.tableConfigsForCodeBooks.map((it) => {
				if (it.id == this.selectedCodeBook.id) {
					const result = it.dataQualityCheckConfig?.result;
					it.dataQualityCheckConfig = config;
					it.dataQualityCheckConfig.result = result;
					updatedConfig = it.dataQualityCheckConfig;
				}

				return it;
			});

			this.selectedCodeBook.dataQualityCheckConfig = updatedConfig;
		},
		setDataQualityCheckResult(result) {
			let generatedCustomClasses = [];
			this.tableConfigsForCodeBooks.map((it) => {
				if (it.id == this.selectedCodeBook.id) {
					it.dataQualityCheckConfig.result = result;
					generatedCustomClasses = this.generateCustomClassesFromCheckResult(result);
					it.tableConfig.styling.customClasses = [...it.tableConfig.styling.customClasses, ...generatedCustomClasses];
				}

				return it;
			});

			this.selectedCodeBook.dataQualityCheckConfig.result = result;
			this.selectedCodeBook.tableConfig.styling.customClasses = [
				...this.selectedCodeBook.tableConfig.styling.customClasses,
				...generatedCustomClasses,
			];
		},
		generateCustomClassesFromCheckResult(result) {
			let customClasses = [];

			// TODO: Group error classes more efficiently
			result.errors.forEach((error) => {
				customClasses.push({
					className: 'du-cell-error',
					colRef: error.colRef,
					rowRef: error.rowRef,
				});
			});

			result.warnings.forEach((warning) => {
				customClasses.push({
					className: 'du-cell-warning',
					colRef: warning.colRef,
					rowRef: warning.rowRef,
				});
			});

			if (customClasses.find((it) => it.rowRef != null && !it.colRef)) {
				customClasses.push({
					className: 'du-spacer',
					colRef: null,
					rowRef: 'spacer',
				});
			}

			return customClasses;
		},
		clickedErrorIcon(ref) {
			this.detailedInfo = {
				type: 'ERROR',
				values: this.selectedCodeBook.dataQualityCheckConfig.result.errors.filter(
					(error) => error.rowRef?.toString() == ref.rowRef && error.colRef == ref.colRef
				),
			};
		},
		clickedWarningIcon(ref) {
			this.detailedInfo = {
				type: 'WARNING',
				values: this.selectedCodeBook.dataQualityCheckConfig.result.warnings.filter(
					(warning) => warning.rowRef?.toString() == ref.rowRef && warning.colRef == ref.colRef
				),
			};
		},
		uploadData() {
			if (!this.isUploading) {
				this.isUploading = true;

				let uploadData = [];

				this.tableConfigsForCodeBooks.forEach((it) => {
					const mappingColumn = it.mappings[0].rows;
					let dataGroup = {
						codeBookID: it.id,
						dataQualityCheckConfig: {
							answerSeparator: it.dataQualityCheckConfig.answerSeparator,
							mappingSeparator: it.dataQualityCheckConfig.mappingSeparator,
							...it.dataQualityCheckConfig.checkConfig,
						},
						values: [mappingColumn],
					};

					let rows = [];
					it.tableConfig.data.columns.forEach((col) => {
						const colRef = col.ref.join('');

						// Only loop through columns that are included in the codebook
						if (mappingColumn.findIndex((it) => it == colRef) != -1) {
							it.tableConfig.data.values.forEach((row, idx) => {
								if (rows[idx]) rows[idx].push(row[colRef]);
								else if (!rows[idx]) rows.push([row[colRef]]);
							});
						}
					});
					dataGroup.values = [...dataGroup.values, ...rows];
					uploadData.push(dataGroup);
				});

				window.setTimeout(() => {
					this.$network.postData(`/api/data/studies/${this.selectedStudy.id}`, uploadData, null, (err, data) => {
						try {
							// TODO: Remove mocked data
							// if (!err) ...
							if (err) {
								this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('duUploadedDataSuccessfully'));
								this.$router.push({ name: ROUTE.PROFILE });
							} else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
						} catch (error) {
							this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
						} finally {
							this.isUploading = false;
							window.dispatchEvent(new Event('resize'));
						}
					});
				}, 1000);
			}
		},
		resetView() {
			this.selectedStudy = null;
			this.selectedCodeBook = null;
			this.tableConfigsForCodeBooks = [];
			this.mappingColumn = null;
			this.translationColumn = null;
			this.selectedItem = null;
			this.assignedMetaItem = null;
			this.detailedInfo = null;
			this.dataTableConfig.data.columns = [];
			this.dataTableConfig.data.values = [];
		},
	},
};
</script>

<style scoped>
.du-wrap-content {
	width: 100%;
	padding-bottom: 20px;
	position: relative;
}

.du-wrap-studies-table {
	padding: 2px;
	position: relative;
	overflow: hidden;
	box-sizing: border-box;
}

.du-wrap-selected-study {
	width: 100%;
	margin-top: 20px;
}

.du-wrap-upload button {
	padding: 5px 10px;
	font-size: 18px;
}

.du-wrap-data-table {
	width: 100%;
}

.du-wrap-row-mapping {
	width: 100%;
	margin: 10px 0px;
	display: flex;
	justify-content: flex-start;
	align-items: flex-end;
	flex-flow: wrap;
	gap: 5px 10px;
}

.du-wrap-mapping {
	width: 300px;
	height: 45px;
}

.du-wrap-mapping label {
	font-size: 16px;
}

.du-wrap-mapping select {
	width: 100%;
	padding: 5px 10px;
	display: block;
	font-size: 15px;
}

.du-wrap-quality-check-button {
	flex: 1 1 200px;
	display: flex;
	justify-content: flex-start;
	align-items: center;
}

.du-wrap-quality-check-button button {
	padding: 5px 10px;
	font-size: 18px;
}

.du-wrap-data-quality-check {
	width: 100%;
	height: 100%;
	padding: 10px 30px;
	position: fixed;
	top: 0px;
	left: 0px;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: column;
	z-index: 2;
	box-sizing: border-box;
	background-color: var(--main-color-dark-80);
}

.du-tab-view {
	width: 100%;
	margin: 10px 0px 0px 0px;
	display: flex;
	justify-content: flex-start;
	align-items: flex-start;
	gap: 5px;
}

.du-tab {
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

.du-tab:hover {
	cursor: pointer;
	background-color: var(--main-color-5);
}

.du-current-tab {
	background-color: var(--main-color-5);
}

.du-data-table {
	position: relative;
}

.du-wrap-detailed-info {
	width: 100%;
	height: 100%;
	position: absolute;
	top: 0px;
	left: 0px;
	display: flex;
	justify-content: center;
	align-items: center;
	background-color: var(--main-color-dark-80);
}

.du-detailed-info {
	max-width: 500px;
	max-height: 80%;
	padding: 10px 20px;
	border: 2px solid var(--main-color-light);
	border-radius: 10px;
	text-align: center;
	background-color: var(--main-color-1);
}

.du-detailed-info svg {
	font-size: 30px;
}

.du-detailed-info div {
	width: 100%;
	margin-top: 10px;
	border-top: 1px solid var(--main-color-light);
	text-align: start;
}

.du-detailed-info div p {
	margin-top: 5px;
}

.du-wrap-bottom {
	max-width: 800px;
	margin: 20px auto 0px auto;
	text-align: center;
}

.du-wrap-data-status p {
	width: 100%;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: column;
	gap: 10px;
	font-size: 18px;
}

.du-wrap-data-status svg {
	margin: 0px 10px;
	font-size: 30px;
}

.du-error-svg * {
	color: var(--main-color-error);
}

.du-warning-svg * {
	color: var(--main-color-warn);
}

.du-info-svg * {
	color: var(--main-color-info);
}

.du-success-svg * {
	color: var(--main-color-success);
}

.du-wrap-buttons {
	width: 100%;
	margin: 20px 0px;
	text-align: center;
}

.du-wrap-buttons button {
	padding: 5px 10px;
	font-size: 18px;
}
</style>

<style>
.du-column-deleted {
	text-align: center;
	background-color: var(--main-color-disabled) !important;
	color: var(--main-color-light) !important;
	cursor: default;
	pointer-events: none;
	user-select: none;
}

.du-column-deleted svg {
	visibility: hidden;
}

/* .du-cell-error {
	background-color: var(--main-color-error-80) !important;
}

.du-cell-warning {
	background-color: var(--main-color-warn-80) !important;
} */

.du-cell-error .ta-error-icon {
	width: 30px !important;
	display: inline-block !important;
}

.du-cell-warning .ta-warning-icon {
	width: 30px !important;
	display: inline-block !important;
}

.du-spacer {
	min-width: 35px !important;
}
</style>
