<template>
	<div class="dv-wrap-content">
		<h2>{{ $t('dvAvailableStudies') }}</h2>
		<div class="dv-wrap-submissions">
			<LoadingSpinner v-if="isLoading" :wrapper-class="'dv-wrap-submissions'" />
			<Table :config="studyConfig" @selectItem="selectStudy" />
		</div>
		<div v-if="selectedStudy" class="dv-wrap-submission-details">
			<h2>{{ $t('dvSubmissionDetails') }}</h2>
			<StudyInfo v-if="selectedStudy.studyInfo" :disabled="true" :studyInfo="selectedStudy.studyInfo" />
		</div>
		<div v-if="selectedStudy" class="dv-wrap-data-table">
			<h2>{{ $t('dvSubmittedData') }}</h2>
			<div v-if="selectedCodeBook" class="dv-wrap-row-mapping">
				<div class="dv-wrap-mapping">
					<label>{{ $t('dvColumnIdentifier') }}</label>
					<select v-model="usedIdentifier" @change="setIdentifierForCodeBook">
						<option v-for="identifier in selectedCodeBook.identifierForCodebook" :key="identifier" :value="identifier">
							{{ identifier === 'id' ? 'ID' : identifier }}
						</option>
					</select>
				</div>
				<div class="dv-wrap-quality-check-button">
					<button class="app-default-btn" @click="showDataQualityCheck = true">
						{{ $t('dvCheckDataQuality') }} <fai icon="fa-solid fa-magnifying-glass-chart" />
					</button>
				</div>
			</div>
			<div v-if="showDataQualityCheck" class="dv-wrap-data-quality-check" @click="showDataQualityCheck = false">
				<DataQualityCheck
					:codeBook="selectedCodeBook"
					:mode="dqcmEnum.VIEW"
					@click.stop=""
					@close="showDataQualityCheck = false"
					@checkResult="setDataQualityCheckResult"
				/>
			</div>
			<div class="dv-tab-view">
				<div
					v-for="codeBook in selectedStudy.codeBooks"
					:key="codeBook.id"
					:class="['dv-tab', codeBook.id == selectedCodeBook?.id ? 'dv-current-tab' : '']"
					@click="selectCodeBook(codeBook.id)"
				>
					{{ codeBook.name }}
				</div>
			</div>
			<div v-for="config in tableConfigsForCodeBooks" :key="config.id" class="dv-data-table">
				<Table
					v-if="config.id == selectedCodeBook.id && config.tableConfig"
					:config="config.tableConfig"
					@clickedErrorIcon="clickedErrorIcon"
					@clickedWarningIcon="clickedWarningIcon"
				/>
				<div
					v-if="config.id == selectedCodeBook.id && config.tableConfig && detailedInfo"
					class="dv-wrap-detailed-info"
					@click="detailedInfo = null"
				>
					<div @click.stop="" class="dv-detailed-info">
						<fai v-if="detailedInfo.type == 'ERROR'" icon="fas fa-circle-xmark" class="dv-error-svg" />
						<fai v-else-if="detailedInfo.type == 'WARNING'" icon="fas fa-triangle-exclamation" class="dv-warning-svg" />
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
	</div>
</template>

<script>
import Table from '@/components/general/Table.vue';
import StudyInfo from '@/components/upload/StudyInfo.vue';
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
import { DATA_QUALITY_CHECK_MODE, ROUTE, TOAST_TYPE } from '@/enums/enums';
import studys from '@/assets/dummy/dataOverview.json';
import { studyConfig } from '@/components/dataView/studyConfig.js';
import dataViewStudyDataFirst from '@/assets/dummy/dataViewStudyDataFirst.json';
import dataViewStudyDataSecond from '@/assets/dummy/dataViewStudyDataSecond.json';
import dataViewStudyDataThird from '@/assets/dummy/dataViewStudyDataThird.json';
import { dataViewTableConfig } from '@/components/dataView/dataViewTableConfig.js';
import DataQualityCheck from '@/components/upload/DataQualityCheck.vue';

/**
 * @vuese
 * @group DataViewer
 * Provides data inspection and quality assurance tools to the user
 */
export default {
	name: 'DataView',
	components: { Table, StudyInfo, LoadingSpinner, DataQualityCheck },
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
			studys: studys,
			studyConfig: studyConfig,
			studyID: null,
			dataViewStudyDataFirst: dataViewStudyDataFirst,
			dataViewStudyDataSecond: dataViewStudyDataSecond,
			dataViewStudyDataThird: dataViewStudyDataThird,
			dataTableConfig: dataViewTableConfig,
			selectedStudy: null,
			tableConfigsForCodeBooks: [],
			selectedCodeBook: null,
			showDataQualityCheck: false,
			usedIdentifier: null,
			detailedInfo: null,
		};
	},
	computed: {},
	created() {
		this.queryStudys();
	},
	mounted() {},
	beforeDestroy() {},
	methods: {
		queryStudys() {
			this.isLoading = true;

			this.$network.getData(`/api/study?for_route=VIEW`, null, null, (err, data) => {
				try {
					if (!err) this.studyConfig.data.values = data;
					else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.isLoading = false;
				}
			});
		},
		selectStudy(study) {
			this.resetView();
			if (study) {
				this.isLoading = true;

				this.studyID = study.id;
				this.$router.push({ name: ROUTE.DATA_VIEW, params: { studyID: study.id } });

				this.$network.getData(`/api/study/${this.studyID}`, null, null, (err, data) => {
					try {
						if (!err) {
							this.selectedStudy = data;
							this.setupDataTable();
						} else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
					} catch (error) {
						this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
					} finally {
						this.isLoading = false;
					}
				});
			}
		},
		setupDataTable() {
			this.selectedCodeBook = null;
			this.usedIdentifier = null;
			this.tableConfigsForCodeBooks = [];

			let tableConfigsForCodeBooks = [];

			this.selectedStudy.codeBooks.map((it) => {
				it.dataQualityCheckConfig = this.mapDataQualityCheckConfig(it.dataQualityCheckConfig);
				return it;
			});

			this.selectedStudy.codeBooks.forEach((codeBook) => {
				const propertyValues = {};

				codeBook.columns.forEach((col) => {
					for (const key in col.item) {
						if (!propertyValues[key]) propertyValues[key] = new Set();

						propertyValues[key].add(col.item[key]);
					}
				});

				const identifierForCodebook = [...Object.keys(propertyValues).filter((key) => propertyValues[key].size === codeBook.columns.length)];

				const usedIdentifier =
					identifierForCodebook[0] == 'id' && identifierForCodebook.length > 1 ? identifierForCodebook[1] : identifierForCodebook[0];

				const { columns: columns, rows: rows } = this.computeColumnsAndRows(codeBook, usedIdentifier);

				let dataTableConfig = JSON.parse(JSON.stringify(this.dataTableConfig));
				dataTableConfig.data.columns = columns;
				dataTableConfig.data.values = rows;

				const mappings = codeBook.meta
					.map((it) => {
						return {
							id: it.idx,
							tag: it.tag,
							name: it.header,
							rows: it.rows,
							assignedItem: it.assignedMetaField,
						};
					})
					.sort((a, b) => a.name.localeCompare(b.name));

				tableConfigsForCodeBooks.push({
					id: codeBook.id,
					name: codeBook.name,
					tableConfig: dataTableConfig,
					identifierForCodebook: identifierForCodebook,
					usedIdentifier: usedIdentifier,
					dataQualityCheckConfig: codeBook.dataQualityCheckConfig,
					mappings: mappings.filter((it) => new Set(it.rows).size == it.rows.length),
					linkedData: codeBook.columns.sort((a, b) => a.idx - b.idx).map((col) => col.linkedItem),
					data: mappings,
					// meta: [...Object.keys(propertyValues)],
				});
			});

			this.selectedCodeBook = tableConfigsForCodeBooks[0];
			this.usedIdentifier = tableConfigsForCodeBooks[0].usedIdentifier;
			this.tableConfigsForCodeBooks = tableConfigsForCodeBooks;
		},
		mapDataQualityCheckConfig(dataQualityCheckConfig) {
			return {
				checkConfig: {
					VALUE_TYPE: dataQualityCheckConfig.valueType,
					VALUE_RANGE_MIN: dataQualityCheckConfig.valueRangeMin,
					VALUE_RANGE_MAX: dataQualityCheckConfig.valueRangeMax,
					VALUE_MAPPING: dataQualityCheckConfig.valueMapping,
					VALUE_REQUIRED: dataQualityCheckConfig.valueRequired,
					EMPTY_VALUES: dataQualityCheckConfig.emptyValues,
					EMPTY_ROWS: dataQualityCheckConfig.emptyRows,
					EMPTY_COLUMNS: dataQualityCheckConfig.emptyColumns,
				},
				mappingSeparator: dataQualityCheckConfig.mappingSeparator,
				answerSeparator: dataQualityCheckConfig.answerSeparator,
			};
		},
		selectCodeBook(id) {
			this.selectedCodeBook = this.tableConfigsForCodeBooks.find((it) => it.id == id);
			this.usedIdentifier = this.selectedCodeBook.usedIdentifier;
		},
		setIdentifierForCodeBook() {
			const codeBook = this.selectedStudy.codeBooks.find((it) => it.id == this.selectedCodeBook.id);
			const { columns: columns, rows: rows } = this.computeColumnsAndRows(codeBook, this.usedIdentifier);

			this.tableConfigsForCodeBooks.map((it) => {
				if (it.id == this.selectedCodeBook.id) {
					it.usedIdentifier = this.usedIdentifier;
					it.tableConfig.data.columns = columns;
					it.tableConfig.data.values = rows;
				}
				return it;
			});
		},
		computeColumnsAndRows(codebook, usedIdentifier) {
			let columns = [{ ref: ['rowID'], text: this.$t('dvRowID') }];
			let rows = [];
			const useID = usedIdentifier == 'id';

			// Correctly orders the columns and rows
			const sortedColumns = codebook.columns.sort((a, b) => a.idx - b.idx);
			const sortedRows = codebook.rows.sort((a, b) => a.idx - b.idx);

			sortedColumns.forEach((col, idx) => {
				const identifier = useID ? col.item.id.toString() : col.item[usedIdentifier];

				columns.push({
					ref: [identifier],
					text: identifier,
					formatter: (value) => {
						return this.$global.valueIsNotAvailable(value, true, false) ? '-' : value;
					},
				});

				sortedRows.forEach((row, rowIdx) => {
					if (!rows[rowIdx]) rows.push({ rowID: rowIdx + 1 });
					rows[rowIdx][identifier] = row.cells[idx];
				});
			});

			return { columns: columns, rows: rows };
		},
		setDataQualityCheckResult(result) {
			let generatedCustomClasses = [];
			this.tableConfigsForCodeBooks.map((it) => {
				if (it.id == this.selectedCodeBook.id) {
					it.dataQualityCheckConfig.result = result;
					generatedCustomClasses = this.generateCustomClassesFromCheckResult(result);

					const existingClasses = it.tableConfig.styling?.customClasses || [];

					it.tableConfig.styling = {
						customClasses: [...existingClasses, ...generatedCustomClasses],
					};
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
					className: 'dv-cell-error',
					colRef: error.colRef,
					rowRef: error.rowRef,
				});
			});

			result.warnings.forEach((warning) => {
				customClasses.push({
					className: 'dv-cell-warning',
					colRef: warning.colRef,
					rowRef: warning.rowRef,
				});
			});

			if (customClasses.find((it) => it.rowRef != null && !it.colRef)) {
				customClasses.push({
					className: 'dv-spacer',
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
		navigateTo(dest) {
			this.$router.push({ name: dest });
		},
		resetView() {
			this.selectedStudy = null;
			this.selectedCodeBook = null;
			this.tableConfigsForCodeBooks = [];
			this.detailedInfo = null;
		},
	},
};
</script>

<style scoped>
.dv-wrap-content {
	width: 100%;
	position: relative;
}
.dv-wrap-content h2 {
	margin: 10px 0px 20px 0px;
	text-decoration: underline;
	font-weight: normal;
}
.dv-wrap-submissions {
	margin: 10px 0px;
	padding: 2px;
	position: relative;
	overflow: hidden;
}
.dv-wrap-submission-details {
	width: 100%;
	padding: 10px 0px 20px 0px;
}
.dv-wrap-quality-check-button {
	flex: 1 1 200px;
	display: flex;
	justify-content: flex-start;
	align-items: center;
}
.dv-wrap-quality-check-button button {
	padding: 5px 10px;
	font-size: 17px;
}
.dv-wrap-data-quality-check {
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
.dv-wrap-row-mapping {
	width: 100%;
	margin: 10px 0px;
	display: flex;
	justify-content: flex-start;
	align-items: flex-end;
	flex-flow: wrap;
	gap: 5px 10px;
}
.dv-wrap-mapping {
	width: 300px;
	height: 46px;
}
.dv-wrap-mapping label {
	font-size: 16px;
	padding-left: 3px;
}

.dv-wrap-mapping select {
	width: 100%;
	padding: 5px 10px;
	display: block;
	font-size: 15px;
}
.dv-cell-error .ta-error-icon {
	width: 30px !important;
	display: inline-block !important;
}
.dv-cell-warning .ta-warning-icon {
	width: 30px !important;
	display: inline-block !important;
}
.dv-spacer {
	min-width: 30px !important;
}
.dv-wrap-data-table {
	width: 100%;
	padding-bottom: 20px;
}
.dv-tab-view {
	width: 100%;
	margin: 10px 0px 0px 0px;
	display: flex;
	justify-content: flex-start;
	align-items: flex-start;
	gap: 5px;
}
.dv-tab {
	width: 200px;
	padding: 5px 10px;
	border: 2px solid var(--main-color-dark);
	border-radius: 10px 10px 0px 0px;
	text-align: center;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
	background-color: var(--main-color-4);
	color: var(--main-color-dark);
}
.dv-tab:hover {
	cursor: pointer;
	background-color: var(--main-color-5);
}
.dv-current-tab {
	background-color: var(--main-color-5);
}

.dv-data-table {
	position: relative;
}

.dv-wrap-detailed-info {
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

.dv-detailed-info {
	max-width: 500px;
	max-height: 80%;
	padding: 10px 20px;
	border: 2px solid var(--main-color-light);
	border-radius: 10px;
	text-align: center;
	background-color: var(--main-color-1);
}

.dv-detailed-info svg {
	font-size: 30px;
}

.dv-detailed-info div {
	width: 100%;
	margin-top: 10px;
	border-top: 1px solid var(--main-color-light);
	text-align: start;
}

.dv-detailed-info div p {
	margin-top: 5px;
}

.dv-error-svg * {
	color: var(--main-color-error);
}

.dv-warning-svg * {
	color: var(--main-color-warn);
}

.dv-info-svg * {
	color: var(--main-color-info);
}

.dv-success-svg * {
	color: var(--main-color-success);
}
</style>

<style>
.dv-column-deleted {
	text-align: center;
	background-color: var(--main-color-disabled) !important;
	color: var(--main-color-light) !important;
	cursor: default;
	pointer-events: none;
	user-select: none;
}

.dv-column-deleted svg {
	visibility: hidden;
}

/* .dv-cell-error {
	background-color: var(--main-color-error-80) !important;
}

.dv-cell-warning {
	background-color: var(--main-color-warn-80) !important;
} */

.dv-cell-error .ta-error-icon {
	width: 30px !important;
	display: inline-block !important;
}

.dv-cell-warning .ta-warning-icon {
	width: 30px !important;
	display: inline-block !important;
}

.dv-spacer {
	min-width: 30px !important;
}
</style>
