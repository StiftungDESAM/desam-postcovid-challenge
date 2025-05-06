<template>
	<div class="dqc-wrap-content">
		<LoadingSpinner v-if="isLoading" :wrapperClass="'dqc-wrap-content'" />
		<div class="dqc-wrap-tabs">
			<div :class="['dqc-tab', activeTab == 'LEFT' ? 'dqc-active-tab' : '']" @click="setActiveTab('LEFT')">{{ $t('dqcQualityCheck') }}</div>
			<div :class="['dqc-tab', activeTab == 'RIGHT' ? 'dqc-active-tab' : '']" @click="setActiveTab('RIGHT')">
				{{ $t('dqcQualityCheckResults') }}
			</div>
		</div>
		<div class="dqc-wrap-slider">
			<div class="dqc-wrap-container" :style="{ transform: `translateX(${activeTab === 'RIGHT' ? '-50%' : '0%'})` }">
				<div class="dqc-wrap-check-setup">
					<h2>{{ $t('dqcDataQualityCheckForCodeBook', { codeBook: codeBook.name }) }}</h2>
					<div v-if="!codeBook.tableConfig" class="dqc-wrap-stats">{{ $t('dqcNoDataUploaded') }}</div>
					<div v-if="codeBook.tableConfig" class="dqc-wrap-quality-check-configuration">
						<h3>{{ $t('dqcRequiredChecks') }}</h3>
						<em v-if="mode == dqcmEnum.UPLOAD">{{ $t('dqcSelectionExplanation') }}</em>
						<em v-else>{{ $t('dqcSelectionExplanationView') }}</em>
						<div class="dqc-wrap-required-checks">
							<div v-for="check in requiredChecks" :key="check" class="dqc-wrap-check">
								<div v-if="mode == dqcmEnum.UPLOAD" class="dqc-wrap-select">
									<label>{{ $t(check) }}</label>
									<!--<select @change="setMetaFieldForCheck($event, check)" v-model="checkConfig[check]" required>-->
									<select :value="stringifiedValue(checkConfig[check])" @change="setMetaFieldForCheck($event, check)" required>
										<option value="" default selected hidden>{{ $t('dqcNoMetaSelected') }}</option>
										<option value="REMOVE">{{ $t('dqcDeselectCurrentOption') }}</option>
										<option value="NONE">{{ $t('dqcNoMetaAssignment') }}</option>
										<option
											v-for="meta in codeBook.data"
											:key="meta.tag"
											:value="meta.assignedMetaField?.tag || meta.tag"
											:disabled="optionAlreadyUsed(meta.assignedMetaField?.tag || meta.tag)"
										>
											{{ meta.name }} <span v-if="meta.assignedMetaField">({{ meta.assignedMetaField.name }})</span>
										</option>
									</select>
								</div>
								<div v-else-if="mode == dqcmEnum.VIEW" class="dqc-wrap-select">
									<!-- TODO: Check with actual data -->
									<label>{{ $t(check) }}</label>
									<!--<select @change="setMetaFieldForCheck($event, check)" v-model="checkConfig[check]" :disabled="true">-->
									<select
										:value="stringifiedValue(checkConfig[check])"
										@change="setMetaFieldForCheck($event, check)"
										:disabled="true"
									>
										<option value="" default selected hidden>{{ $t('dqcNoMetaSelected') }}</option>
										<option value="REMOVE">{{ $t('dqcDeselectCurrentOption') }}</option>
										<option value="NONE">{{ $t('dqcNoMetaAssignment') }}</option>
										<option value="NOT_AVAILABLE" disabled>{{ $t('dqcNotAvailable') }}</option>
										<option
											v-for="meta in codeBook.data"
											:key="meta.tag"
											:value="meta.tag"
											:disabled="optionAlreadyUsed(meta.tag)"
										>
											{{ meta.name }} <span v-if="meta.assignedMetaField">({{ meta.assignedMetaField.name }})</span>
										</option>
									</select>
								</div>
								<div v-if="check == qcmEnum.VALUE_MAPPING && checkConfig.VALUE_MAPPING !== null" class="dqc-wrap-split">
									<label>{{ $t('dqcMappingSplitBy') }}</label>
									<select v-model="mappingSeparator" @change="updateConfig" required :disabled="mode == dqcmEnum.VIEW">
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
								<div v-if="check == qcmEnum.VALUE_MAPPING && checkConfig.VALUE_MAPPING !== null" class="dqc-wrap-split">
									<label>{{ $t('dqcAnswerSplitBy') }}</label>
									<select v-model="answerSeparator" @change="updateConfig" required :disabled="mode == dqcmEnum.VIEW">
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
								<!-- <div v-if="check == qcmEnum.VALUE_BRANCHING" class="dqc-wrap-branching">
						<label>{{ $t('dqcBranchIdentifier') }}</label>
						<select v-model="branchIdentifier" @change="updateConfig" required>
							<option value="" disabled selected hidden>{{ $t('dqcSelectBranchIdentifier') }}</option>
							<option :value="branchEnum.ONLY_NUMBER">{{ $t('dqcOnlyNumber') }}</option>
							<option :value="branchEnum.ONLY_STRING">{{ $t('dqcOnlyText') }}</option>
							<option :value="branchEnum.FULL_STRING">{{ $t('dqcFullText') }}</option>
						</select>
					</div> -->
							</div>
						</div>
						<div class="dqc-wrap-optional-checks">
							<h3>{{ $t('dqcOptionalChecks') }}</h3>
							<div v-for="check in optionalChecks" :key="check" class="dqc-wrap-check">
								<input
									:id="check"
									type="checkbox"
									:checked="checkConfig[check]"
									@change="setMetaFieldForCheck($event, check)"
									:disabled="mode == dqcmEnum.VIEW"
								/>
								<label :for="check">{{ $t(check) }}</label>
							</div>
						</div>
					</div>
					<div class="dqc-wrap-buttons" v-if="codeBook.tableConfig">
						<button class="app-default-btn" @click="$emit('close')">{{ $t('dqcCancel') }}</button>
						<button :class="[canPerformCheck ? 'app-default-btn' : 'app-disabled-btn']" @click="performDataQualityCheck">
							{{ $t('dqcPerformCheck') }}
						</button>
					</div>
				</div>
				<div class="dqc-wrap-check-result">
					<h2>{{ $t('dqcDataQualityCheckResultsForCodeBook', { codeBook: codeBook.name }) }}</h2>
					<p v-if="!checkResult" class="dqc-no-check-results">{{ $t('dqcNoQualityCheckResults') }}</p>
					<div v-else class="dqc-wrap-summary">
						<div class="dqc-summary-element">
							<fai icon="fas fa-circle-xmark" class="dqc-error-svg" />
							<p>{{ summedErrors }}</p>
						</div>
						<div class="dqc-summary-element">
							<fai icon="fas fa-triangle-exclamation" class="dqc-warning-svg" />
							<p>{{ summedWarnings }}</p>
						</div>
						<div class="dqc-summary-element">
							<fai icon="fas fa-circle-info" class="dqc-info-svg" />
							<p>{{ summedInfo }}</p>
						</div>
					</div>
					<div v-if="checkResult" class="dqc-wrap-section">
						<h3 class="dqc-error-heading"><fai icon="fas fa-circle-xmark" />{{ $t('dqcDataErrors') }}</h3>
						<p v-if="checkResult.errors.length == 0" class="dqc-success-text">
							{{ $t('dqcNoErrorsFound') }}
						</p>
						<div v-else>
							<div v-for="error in Object.keys(groupedErrors)" :key="error" class="dqc-group-errors">
								<p class="dqc-summary-text" @click="!shownData.includes(error) ? showData(error) : hideData(error)">
									{{ $t(error) }}: {{ groupedErrors[error].length }}
									<fai v-if="!shownData.includes(error)" icon="fas fa-chevron-down" />
									<fai v-else icon="fas fa-chevron-up" />
								</p>
								<transition name="expand">
									<div v-if="shownData.includes(error)" class="dqc-wrap-detailed-checks">
										<div v-for="(err, idx) in groupedErrors[error]" :key="idx">
											<span v-html="$t('dqcRowAndColumn', { row: err.rowRef, col: err.colRef })"></span>
											<span v-html="$t(`${err.text}_TEXT`, err.textOptions)"></span>
										</div>
									</div>
								</transition>
							</div>
						</div>
					</div>
					<div v-if="checkResult" class="dqc-wrap-section">
						<h3 class="dqc-warning-heading"><fai icon="fas fa-triangle-exclamation" />{{ $t('dqcDataWarnings') }}</h3>
						<p v-if="checkResult.warnings.length == 0" class="dqc-success-text">
							{{ $t('dqcNoWarningsFound') }}
						</p>
						<div v-else>
							<div v-for="warning in Object.keys(groupedWarnings)" :key="warning" class="dqc-group-warnings">
								<p class="dqc-summary-text" @click="!shownData.includes(warning) ? showData(warning) : hideData(warning)">
									{{ $t(warning) }}: {{ groupedWarnings[warning].length }}
									<fai v-if="!shownData.includes(warning)" icon="fas fa-chevron-down" />
									<fai v-else icon="fas fa-chevron-up" />
								</p>
								<transition name="expand">
									<div v-if="shownData.includes(warning)" class="dqc-wrap-detailed-checks">
										<div v-for="(warn, idx) in groupedWarnings[warning]" :key="idx">
											<span v-html="$t('dqcRowAndColumn', { row: warn.rowRef, col: warn.colRef })"></span>
											<span v-html="$t(`${warn.text}_TEXT`, warn.textOptions)"></span>
										</div>
									</div>
								</transition>
							</div>
						</div>
					</div>
					<div v-if="checkResult" class="dqc-wrap-section">
						<h3 class="dqc-info-heading"><fai icon="fas fa-circle-info" />{{ $t('dqcInfo') }}</h3>
						<div class="dqc-wrap-data-info">
							<p>{{ $t('dqcAmountRows') }} {{ codeBook.tableConfig.data.values.length }}</p>
							<p>{{ $t('dqcAmountCols') }} {{ codeBook.tableConfig.data.columns.length }}</p>
							<p>
								{{ $t('dqcAmountCells') }}
								{{ codeBook.tableConfig.data.values.length * codeBook.tableConfig.data.columns.length }}
							</p>
						</div>
						<div>
							<div v-for="info in Object.keys(groupedInfo)" :key="info" class="dqc-group-info">
								<div v-for="(i, idx) in groupedInfo[info]" :key="idx">
									{{ $t(`${i.text}_TEXT`, i.textOptions) }}
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import DataQualityCheckWorker from '@/worker/dataQualityCheckWorker.js?worker';
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
import { QUALITY_CHECK_METHOD, MAPPING_SPLIT, BRANCHING_FORMAT, DATA_QUALITY_CHECK_MODE } from '@/enums/enums';
/**
 * @group Upload
 * Checks the data quality of the uploaded study data by the code book metadata
 */
export default {
	name: 'DataQualityCheck',
	components: { LoadingSpinner },
	emits: ['close', 'setConfig', 'checkResult'],
	props: {
		codeBook: {
			type: Object,
			required: true,
		},
		mode: {
			type: String,
			required: true,
		},
	},
	watch: {},
	setup() {
		const qcmEnum = QUALITY_CHECK_METHOD;
		const splitEnum = MAPPING_SPLIT;
		const branchEnum = BRANCHING_FORMAT;
		const dqcmEnum = DATA_QUALITY_CHECK_MODE;

		return { qcmEnum, splitEnum, branchEnum, dqcmEnum };
	},
	data() {
		return {
			isLoading: false,
			activeTab: 'LEFT',
			animation: false,
			requiredChecks: [
				QUALITY_CHECK_METHOD.VALUE_TYPE,
				QUALITY_CHECK_METHOD.VALUE_RANGE_MIN,
				QUALITY_CHECK_METHOD.VALUE_RANGE_MAX,
				QUALITY_CHECK_METHOD.VALUE_MAPPING,
				// QUALITY_CHECK_METHOD.VALUE_BRANCHING,
				QUALITY_CHECK_METHOD.VALUE_REQUIRED,
			],
			optionalChecks: [QUALITY_CHECK_METHOD.EMPTY_VALUES, QUALITY_CHECK_METHOD.EMPTY_ROWS, QUALITY_CHECK_METHOD.EMPTY_COLUMNS],
			checkConfig: {
				// VALUE_TYPE: 'TextValidationTypeORShowSliderNumber',
				// VALUE_RANGE_MIN: 'TextValidationMin',
				// VALUE_RANGE_MAX: 'TextValidationMax',
				// VALUE_MAPPING: 'ChoicesCalculationsORSliderLabels',
				// VALUE_REQUIRED: 'RequiredField',
				VALUE_TYPE: '',
				VALUE_RANGE_MIN: '',
				VALUE_RANGE_MAX: '',
				VALUE_MAPPING: '',
				VALUE_REQUIRED: '',
				// // Currently disabled
				// // VALUE_BRANCHING: '',
				EMPTY_VALUES: true,
				EMPTY_ROWS: true,
				EMPTY_COLUMNS: true,
			},
			// mappingSeparator: 'BAR',
			// answerSeparator: 'SEMICOLON',
			// branchIdentifier: 'ONLY_NUMBER',
			mappingSeparator: '',
			answerSeparator: '',
			branchIdentifier: '',
			checkResult: null,
			shownData: [],
		};
	},
	computed: {
		/*canPerformCheck() {
			return (
				//Object.values(this.checkConfig).filter((it) => it.toString() != '').length == Object.keys(QUALITY_CHECK_METHOD).length &&
				Object.values(this.checkConfig).filter((it) => it !== null && it !== '').length === Object.keys(QUALITY_CHECK_METHOD).length &&
				// this.branchIdentifier &&
				this.answerSeparator &&
				this.mappingSeparator
			);
		},*/
		canPerformCheck() {
			const filledChecks = Object.values(this.checkConfig).filter((val) => {
				if (val == null || val == 'NONE') return true;
				if (val == '') return false;
				return true;
			});

			const expectedChecks = Object.keys(QUALITY_CHECK_METHOD).length;

			if (this.checkConfig.VALUE_MAPPING == null) {
				this.mappingSeparator = null;
				this.answerSeparator = null;
				return filledChecks.length == expectedChecks;
			}
			return filledChecks.length == expectedChecks && this.mappingSeparator && this.answerSeparator;
		},
		groupedErrors() {
			return this.checkResult?.errors?.reduce((acc, error) => {
				if (!acc[error.text]) acc[error.text] = [];

				acc[error.text].push(error);
				return acc;
			}, {});
		},
		summedErrors() {
			if (this.groupedErrors && Object.values(this.groupedErrors).length > 0)
				return Object.values(this.groupedErrors).reduce((a, b) => a + b.length, 0);
			else return 0;
		},
		groupedWarnings() {
			return this.checkResult?.warnings?.reduce((acc, warning) => {
				if (!acc[warning.text]) acc[warning.text] = [];

				acc[warning.text].push(warning);
				return acc;
			}, {});
		},
		summedWarnings() {
			if (this.groupedWarnings && Object.values(this.groupedWarnings).length > 0)
				return Object.values(this.groupedWarnings).reduce((a, b) => a + b.length, 0);
			else return 0;
		},
		groupedInfo() {
			return this.checkResult?.info?.reduce((acc, info) => {
				if (!acc[info.text]) acc[info.text] = [];

				acc[info.text].push(info);
				return acc;
			}, {});
		},
		summedInfo() {
			if (this.groupedInfo && Object.values(this.groupedInfo).length > 0)
				return Object.values(this.groupedInfo).reduce((a, b) => a + b.length, 0) + 3;
			else return 0;
		},
	},
	created() {
		if (this.codeBook.dataQualityCheckConfig) {
			this.checkConfig = this.codeBook.dataQualityCheckConfig.checkConfig;
			this.mappingSeparator = this.codeBook.dataQualityCheckConfig.mappingSeparator;
			// this.branchIdentifier = this.codeBook.dataQualityCheckConfig.branchIdentifier;
			this.answerSeparator = this.codeBook.dataQualityCheckConfig.answerSeparator;
			if (this.codeBook.dataQualityCheckConfig.result) this.checkResult = this.codeBook.dataQualityCheckConfig.result;
		}
	},
	mounted() {},
	beforeDestroy() {},
	methods: {
		setActiveTab(tab) {
			if (this.activeTab === tab || this.animation) return;

			this.activeTab = tab;
			this.animation = true;

			setTimeout(() => {
				this.animation = false;
			}, 500);
		},
		setMetaFieldForCheck(e, check) {
			const value = e.target?.checked ?? e.target?.value;
			if (value == 'REMOVE') {
				this.checkConfig[check] = '';
				e.target.value = '';
			} else if (value === 'NONE') {
				this.checkConfig[check] = null;
			} else this.checkConfig[check] = value;
			//console.log('checkConfig:', JSON.stringify(this.checkConfig, null, 2));
			this.updateConfig();
		},
		stringifiedValue(value) {
			if (value === null) {
				return this.mode === this.dqcmEnum.UPLOAD ? 'NONE' : 'NOT_AVAILABLE';
			}
			if (value === '') return '';
			return value.toString();
		},
		optionAlreadyUsed(tag) {
			return Object.values(this.checkConfig).includes(tag);
		},
		performDataQualityCheck() {
			this.isLoading = true;
			this.updateConfig();

			const worker = new DataQualityCheckWorker();
			// const worker = new Worker(new URL('../../worker/dataQualityCheckWorker.js', import.meta.url));

			worker.onmessage = (e) => {
				this.isLoading = false;
				this.checkResult = e.data;
				this.setActiveTab('RIGHT');
				setTimeout(() => {
					this.$emit('checkResult', e.data);
				}, 100);
			};

			worker.postMessage(
				JSON.parse(
					JSON.stringify({
						config: {
							...this.checkConfig,
							// branchIdentifier: this.branchIdentifier,
							mappingSeparator: this.mappingSeparator,
							answerSeparator: this.answerSeparator,
						},
						codeBook: this.codeBook,
						mode: this.mode,
					})
				)
			);
		},
		updateConfig() {
			/*console.log(
				'Updating config with the following data:',
				JSON.stringify(
					{
						checkConfig: this.checkConfig,
						mappingSeparator: this.mappingSeparator,
						answerSeparator: this.answerSeparator,
					},
					null,
					2
				)
			);*/

			this.$emit('setConfig', {
				checkConfig: this.checkConfig,
				// branchIdentifier: this.branchIdentifier,
				mappingSeparator: this.mappingSeparator,
				answerSeparator: this.answerSeparator,
			});
		},
		showData(ref) {
			this.shownData.push(ref);
		},
		hideData(ref) {
			this.shownData = this.shownData.filter((it) => it != ref);
		},
	},
};
</script>

<style scoped>
.dqc-wrap-content {
	max-width: 80vw;
	max-height: 80vh;
	border: 2px solid var(--main-color-light);
	border-radius: 10px;
	overflow-y: auto;
	overflow-x: hidden;
	box-sizing: border-box;
	position: relative;
	background-color: var(--main-color-1);
}

.dqc-wrap-tabs {
	width: 100%;
	height: 30px;
	margin-bottom: 10px;
	display: flex;
	justify-content: center;
	align-items: center;
	gap: 2px;
}

.dqc-tab {
	flex: 1 1 50%;
	padding: 10px 20px;
	text-align: center;
	cursor: pointer;
	transition: background-color 0.5s;
	background-color: var(--main-color-2);
}

.dqc-active-tab {
	background-color: var(--main-color-3);
}

.dqc-wrap-slider {
	width: 100%;
	overflow: hidden;
}

.dqc-wrap-container {
	width: 200%;
	padding: 10px 20px;
	display: flex;
	justify-content: center;
	align-items: stretch;
	gap: 20px;
	box-sizing: border-box;
	transition: transform 0.5s ease;
}

.dqc-wrap-check-setup,
.dqc-wrap-check-result {
	width: 50%;
	display: inline-block;
	box-sizing: border-box;
	overflow: auto;
}

.dqc-no-check-results {
	width: 100%;
	margin: 20px 0px;
	text-align: center;
}

.dqc-wrap-summary {
	width: 100%;
	margin: 20px 0px 10px 0px;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: wrap;
	gap: 10px 20px;
}

.dqc-summary-element {
	text-align: center;
}

.dqc-summary-element p {
	margin: 10px 0px;
	font-size: 35px;
}

.dqc-summary-element svg {
	font-size: 35px;
}

.dqc-error-svg * {
	color: var(--main-color-error);
}

.dqc-warning-svg * {
	color: var(--main-color-warn);
}

.dqc-info-svg * {
	color: var(--main-color-info);
}

.dqc-wrap-content h2 {
	margin-bottom: 10px;
	text-align: center;
}

.dqc-wrap-stats {
	width: 100%;
	margin: 20px 0px;
	font-size: 18px;
	text-align: center;
}

.dqc-wrap-buttons {
	width: 100%;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: wrap;
	gap: 5px 10px;
	text-align: center;
}

.dqc-wrap-quality-check-configuration {
	margin: 10px 0px;
}

.dqc-wrap-quality-check-configuration h3 {
	margin: 10px 0px 5px 0px;
	font-weight: normal;
	text-decoration: underline;
}

.dqc-wrap-check {
	max-width: 100%;
	margin: 10px 0px;
	display: flex;
	justify-content: flex-start;
	align-items: flex-end;
	gap: 10px;
}

.dqc-wrap-optional-checks .dqc-wrap-check {
	margin: 10px 0px;
	align-items: center;
	flex-flow: wrap;
}

.dqc-wrap-select {
	width: calc(100% - 260px);
}

.dqc-wrap-branching,
.dqc-wrap-split {
	min-width: 250px;
}

.dqc-wrap-check div label {
	margin: 10px 0px 5px 2px;
}

select {
	width: 100%;
	margin-top: 5px;
	padding: 5px 10px;
	display: block;
	font-size: 16px;
	background-color: var(--main-color-5);
	color: var(--main-color-dark);
}

select option {
	color: var(--main-color-dark);
}

select:valid {
	background-color: var(--main-color-2);
	color: var(--main-color-light);
}

select:valid option {
	color: var(--main-color-light);
}

select:valid option:disabled {
	color: var(--main-color-dark);
	background-color: var(--main-color-2);
	opacity: 1;
}

select option:disabled {
	color: var(--main-color-dark);
	background-color: var(--main-color-4);
	opacity: 1;
}

.dqc-wrap-optional-checks .dqc-wrap-check label {
	cursor: pointer;
}

.dqc-wrap-buttons button {
	min-width: 200px;
	padding: 5px 10px;
	font-size: 18px;
}

.dqc-wrap-section {
	width: 100%;
	padding: 5px 10px;
	box-sizing: border-box;
}

.dqc-wrap-section h3 {
	width: 100%;
	display: flex;
	justify-content: flex-start;
	align-items: center;
	gap: 10px;
}

.dqc-wrap-data-info p {
	width: fit-content;
	margin-top: 5px;
	font-size: 18px;
	text-align: start;
}

.dqc-error-heading,
.dqc-warning-heading,
.dqc-info-heading {
	margin: 10px 0px;
	font-size: 22px;
	text-decoration: underline;
}

.dqc-success-text {
	font-size: 16px;
}

.dqc-error-heading {
	color: var(--main-color-error);
}

.dqc-warning-heading {
	color: var(--main-color-warn);
}

.dqc-info-heading {
	color: var(--main-color-info);
}

.dqc-error-heading *,
.dqc-warning-heading *,
.dqc-info-heading * {
	color: inherit;
}
.dqc-group-errors {
	margin-top: 10px;
	font-size: 18px;
}

.dqc-group-warnings,
.dqc-group-info {
	margin-top: 5px;
	font-size: 18px;
}

.dqc-summary-text {
	font-weight: bold;
	cursor: pointer;
}

.dqc-wrap-detailed-checks {
	padding-top: 10px;
	max-height: 400px;
	overflow: auto;
}

.dqc-wrap-detailed-checks div {
	margin-bottom: 2px;
}

.dqc-wrap-detailed-checks span {
	font-size: 16px;
}

.expand-enter-active,
.expand-leave-active {
	transition:
		max-height 0.5s ease-out,
		opacity 0.5s ease-out;
	overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
	max-height: 0;
	opacity: 0;
}
.expand-enter-to,
.expand-leave-from {
	max-height: 400px;
	opacity: 1;
}

input:disabled,
select:disabled {
	border: 1px solid var(--main-color-light);
	opacity: 1 !important; /* Prevent disabled select to lose opacity */
	color: var(--main-color-light) !important;
	background-color: var(--main-color-dark);
	cursor: default !important;
}
</style>
