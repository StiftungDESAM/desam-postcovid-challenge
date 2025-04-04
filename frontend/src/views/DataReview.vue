<template>
	<div class="dr-wrap-content">
		<h2>{{ $t('drSubmissions') }}</h2>
		<ConfirmationWindow v-if="confirmationConfig" :config="confirmationConfig" />
		<LoadingSpinner v-if="isUploading" :wrapperClass="'dr-wrap-content'" />
		<div class="dr-wrap-submissions">
			<LoadingSpinner v-if="isLoading" :wrapperClass="'dr-wrap-submissions'" />
			<Table :config="tableConfig" :resetSelected="resetSelected" @selectItem="selectReview" />
		</div>
		<div v-if="selectedReview" class="dr-wrap-submission-details">
			<h2>{{ $t('drSubmissionDetails') }}</h2>
			<StudyInfo :disabled="true" :studyInfo="selectedReview.submissionDetails.studyInfo" />
		</div>
		<div v-if="selectedReview" class="dr-wrap-data-table">
			<h2>{{ $t('drSubmittedData') }}</h2>
			<div class="dr-tab-view">
				<div
					v-for="codeBook in selectedReview.submissionDetails.codeBooks"
					:key="codeBook.id"
					:class="['dr-tab', codeBook.id == selectedCodeBook.id ? 'dr-current-tab' : '']"
					@click="selectCodeBook(codeBook.id)"
				>
					{{ codeBook.name }}
				</div>
			</div>
			<div v-for="config in codeBooksWithData" :key="config.id" class="dr-data-table">
				<Table v-if="config.id == selectedCodeBook.id && config.tableConfig" :config="config.tableConfig" />
			</div>
		</div>
		<h2 v-if="selectedReview">{{ $t('drOntologyChanges') }}</h2>
		<div v-if="selectedReview" class="dr-wrap-viewer">
			<OntologyViewer :rdfData="selectedReview.submissionDetails.dataOntology" :graphType="gtEnum.DATA" />
		</div>
		<div v-if="selectedReview" class="dr-wrap-review-section">
			<h2>{{ $t('drReviewSection') }}</h2>
			<ReviewSection
				:reviewID="selectedReview.id"
				:reviewer="selectedReview.reviewer"
				:reviewDetails="selectedReview.review"
				:userIsReviewerAndNotFinished="reviewCanBeEdited"
				@assignReview="assignReview"
				@updateReview="setReviewStatus"
			/>
		</div>

		<div v-if="selectedReview" class="dr-wrap-buttons">
			<LoadingSpinner v-if="isUpdating" :positioning="'fixed'" />
			<button :class="reviewCanBeSaved ? 'app-default-btn' : 'app-disabled-btn'" @click="saveAsDraft()">
				{{ $t('drSaveAsDraft') }} <fai icon="fas fa-save" />
			</button>
			<button :class="reviewCanBeSaved ? 'app-default-btn' : 'app-disabled-btn'" @click="saveAsDraftAndClose">
				{{ $t('drSaveAsDraftAndClose') }} <fai icon="fas fa-save" />
			</button>
			<button :class="reviewCanBeSaved ? 'app-success-btn' : 'app-disabled-btn'" @click="confirmFinishReview">
				{{ $t('drFinishReview') }} <fai icon="fas fa-paper-plane" />
			</button>
		</div>
	</div>
</template>

<script>
import Table from '@/components/general/Table.vue';
import StudyInfo from '@/components/upload/StudyInfo.vue';
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
import ConfirmationWindow from '@/components/general/ConfirmationWindow.vue';
import ReviewSection from '@/components/review/ReviewSection.vue';
import OntologyViewer from '@/components/ontology/OntologyViewer.vue';
import dataReviews from '@/assets/dummy/dataReviews.json';
import openReview from '@/assets/dummy/openDataReview.json';
import assignedReview from '@/assets/dummy/assignedDataReview.json';
import closedReview from '@/assets/dummy/closedDataReview.json';
import dataOntology from '@/assets/dummy/dataOntology.json';
import { tableConfig } from '@/components/review/dataReviewTableConfig.js';
import { dataTableConfig } from '@/components/review/dataTableConfig.js';
import { GRAPH_TYPE, REVIEW_STATUS, TOAST_TYPE } from '@/enums/enums';
/**
 * @vuese
 * @group DataReview
 * Provides the maintainer with information about the uploaded data and review tools
 */
export default {
	name: 'DataReview',
	components: { Table, LoadingSpinner, ConfirmationWindow, StudyInfo, ReviewSection, OntologyViewer },
	emits: [],
	props: {},
	watch: {},
	setup() {
		const gtEnum = GRAPH_TYPE;
		return { gtEnum };
	},
	data() {
		return {
			isLoading: false,
			isUploading: false,
			isUpdating: false,
			confirmationConfig: null,
			resetSelected: false,
			dataReviews: dataReviews,
			tableConfig: tableConfig,
			dataTableConfig: dataTableConfig,
			openReview: openReview,
			assignedReview: assignedReview,
			closedReview: closedReview,
			dataOntology: dataOntology.rdf,
			currentUser: this.$store.getCurrentUser(),
			selectedReview: null,
			codeBooksWithData: [],
			selectedCodeBook: null,
		};
	},
	computed: {
		reviewCanBeEdited() {
			return (
				this.selectedReview?.reviewer?.email == this.currentUser.credentials.email &&
				this.selectedReview?.submissionStatus == REVIEW_STATUS.ASSIGNED
			);
		},
		reviewCanBeSaved() {
			return this.reviewCanBeEdited && this.selectedReview?.review?.status;
		},
	},
	created() {
		this.queryDataReviews();
	},
	mounted() {},
	beforeDestroy() {},
	methods: {
		queryDataReviews() {
			this.isLoading = true;

			window.setTimeout(() => {
				this.$network.getData(`/api/review/data`, null, null, (err, data) => {
					try {
						// TODO: Remove mocked data
						// if (!err) this.tableConfig.data.values = data;
						if (err) this.tableConfig.data.values = this.dataReviews;
						else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
					} catch (error) {
						this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
					} finally {
						this.isLoading = false;
						window.dispatchEvent(new Event('resize'));
					}
				});
			}, 2000);
		},
		selectReview(review) {
			this.selectedReview = null;

			if (review) {
				this.isLoading = true;

				window.setTimeout(() => {
					this.$network.getData(`/api/review/data/${review.id}`, null, null, (err, data) => {
						try {
							// TODO: Remove mocked data
							// if (!err) this.selectedReview = data;
							if (err) {
								this.selectedReview =
									review.submissionStatus == REVIEW_STATUS.OPEN
										? this.openReview
										: review.submissionStatus == REVIEW_STATUS.ASSIGNED
											? this.assignedReview
											: this.closedReview;
								this.selectedReview.submissionDetails.dataOntology = this.dataOntology;
								this.setupDataTable();
							} else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
						} catch (error) {
							this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
						} finally {
							this.isLoading = false;
						}
					});
				}, 1000);
			}
		},
		setupDataTable() {
			this.selectedCodeBook = null;
			this.codeBooksWithData = [];

			let codeBooksWithData = [];
			this.selectedReview.submissionDetails.codeBooks.forEach((codeBook) => {
				let codeBookConfig = {
					id: codeBook.id,
					name: codeBook.name,
					tableConfig: JSON.parse(JSON.stringify(this.dataTableConfig)),
				};

				let columns = [{ ref: ['rowID'], text: this.$t('drRowID') }];
				let rows = [];

				codeBook.data[0].forEach((it) => {
					columns.push({
						ref: [it],
						text: it,
						formatter: (value) => {
							return this.$global.valueIsNotAvailable(value, true, false) ? '-' : value;
						},
					});
				});

				rows = codeBook.data.slice(1).map((row, index) => {
					let obj = { rowID: index + 1 };
					row.forEach((cell, index) => {
						obj[codeBook.data[0][index]] = cell.trim();
					});
					return obj;
				});

				codeBookConfig.tableConfig.data.columns = columns;
				codeBookConfig.tableConfig.data.values = rows;

				codeBooksWithData.push(codeBookConfig);
			});

			this.selectedCodeBook = codeBooksWithData[0];
			this.codeBooksWithData = codeBooksWithData;
		},
		selectCodeBook(id) {
			this.selectedCodeBook = this.codeBooksWithData.find((it) => it.id == id);
		},
		assignReview() {
			this.selectedReview.submissionStatus = REVIEW_STATUS.ASSIGNED;
			this.selectedReview.reviewer = {
				firstName: this.currentUser.user.firstName,
				lastName: this.currentUser.user.lastName,
				email: this.currentUser.credentials.email,
			};
		},
		setReviewStatus(status) {
			this.selectedReview.review = status;
		},
		saveAsDraft(cb) {
			this.updateReview({ submissionState: REVIEW_STATUS.ASSIGNED, review: this.selectedReview.review }, false, cb);
		},
		saveAsDraftAndClose() {
			this.saveAsDraft(() => {
				this.selectedReview = null;
				this.resetSelected = !this.resetSelected;
				this.queryDataReviews();
			});
		},
		confirmFinishReview() {
			this.confirmationConfig = {
				title: this.$t('drFinishReviewTitle'),
				text: this.$t('drFinishReviewText'),
				cancelButton: {
					class: 'app-default-btn',
					text: this.$t('rsCancel'),
					callback: () => {
						this.confirmationConfig = null;
					},
				},
				confirmButton: {
					class: 'app-success-btn',
					text: this.$t('orFinishReview'),
					callback: () => {
						this.confirmationConfig = null;
						this.finishReview();
					},
				},
			};
		},
		finishReview() {
			this.updateReview({ submissionState: this.selectedReview.review.status, review: this.selectedReview.review }, true, () => {
				this.selectedReview = null;
				this.resetSelected = !this.resetSelected;
				this.queryDataReviews();
			});
		},
		updateReview(update, isFinish, cb) {
			this.isUpdating = true;

			window.setTimeout(() => {
				this.$network.patchData(`/api/review/data/${this.selectedReview.id}`, update, null, (err, data) => {
					try {
						// TODO: Remove mocked data
						// if (!err) {
						if (err) {
							if (isFinish) this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('drFinishedSuccessfully'));
							else this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('drSavedSuccessfully'));
							if (cb) cb();
						} else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
					} catch (error) {
						this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
					} finally {
						this.isUpdating = false;
						window.dispatchEvent(new Event('resize'));
					}
				});
			}, 1000);
		},
	},
};
</script>

<style scoped>
.dr-wrap-content {
	width: 100%;
	margin-bottom: 20px;
	position: relative;
}

.dr-wrap-content h2 {
	margin: 10px 0px 20px 0px;
	text-decoration: underline;
	font-weight: normal;
}

.dr-wrap-submissions {
	margin: 10px 0px;
	padding: 2px;
	position: relative;
	overflow: hidden;
}

.dr-wrap-submission-details {
	width: 100%;
	padding: 10px 0px 20px 0px;
}

.dr-wrap-data-table {
	width: 100%;
	padding-bottom: 20px;
}

.dr-tab-view {
	width: 100%;
	margin: 10px 0px 0px 0px;
	display: flex;
	justify-content: flex-start;
	align-items: flex-start;
	gap: 5px;
}

.dr-tab {
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

.dr-tab:hover {
	cursor: pointer;
	background-color: var(--main-color-5);
}

.dr-current-tab {
	background-color: var(--main-color-5);
}

.dr-data-table {
	position: relative;
}

.dr-wrap-viewer {
	width: 100%;
	height: 80vh;
	min-width: 500px;
	margin: 2px;
	position: relative;
	overflow: hidden;
	border: 1px solid var(--main-color-light);
	box-sizing: border-box;
}

.dr-wrap-review-section {
	flex: 1 1 500px;
	padding-top: 15px;
}

.dr-wrap-buttons {
	width: 100%;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: wrap;
}

.dr-wrap-buttons button {
	min-width: 250px;
	margin: 5px;
	padding: 10px 5px;
	font-size: 17px;
}
</style>
