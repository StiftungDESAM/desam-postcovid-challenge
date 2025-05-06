<template>
	<div class="fv-wrap-content">
		<h2>{{ $t('fvSubmittedStudies') }}</h2>
		<div class="fv-wrap-submissions">
			<LoadingSpinner v-if="isLoading" :wrapperClass="'fv-wrap-submissions'" />
			<Table :config="feedbackConfig" @selectItem="selectReview" :startValue="feedbackID" />
		</div>
		<div v-if="selectedReview" class="fv-wrap-submission-details">
			<h2>{{ $t('fvSubmissionDetails') }}</h2>
			<StudyInfo v-if="selectedReview?.submissionDetails?.studyInfo" :disabled="true" :studyInfo="selectedReview.submissionDetails.studyInfo" />
			<div v-else class="or-no-submission-details">{{ $t('orNoSubmissionDetails') }}</div>
		</div>
		<div v-if="selectedReview?.submissionDetails?.studyInfo" class="fv-wrap-data-table">
			<h2>{{ uploadTypeTitle }}</h2>
			<div class="fv-tab-view">
				<div
					v-for="codeBook in selectedReview.submissionDetails.codeBooks"
					:key="codeBook.id"
					:class="['fv-tab', codeBook.id == selectedCodeBook.id ? 'fv-current-tab ' : '']"
					@click="selectCodeBook(codeBook.id)"
				>
					{{ codeBook.name }}
				</div>
			</div>
			<div v-for="config in codeBooksWithData" :key="config.id">
				<Table v-if="config.id == selectedCodeBook.id && config.tableConfig" :config="config.tableConfig" @selectItem="selectItem" />
			</div>
		</div>
		<div v-if="selectedReview" class="fv-wrap-review-section">
			<div class="fv-place-holder"></div>
			<div class="fv-review-section">
				<h2>{{ $t('frReviewSection') }}</h2>
				<ReviewSection
					v-if="!['OPEN', 'ASSIGNED'].includes(selectedReview.submissionStatus)"
					:reviewID="selectedReview.id"
					:reviewer="selectedReview.reviewer"
					:reviewDetails="selectedReview.review"
					:userIsReviewerAndNotFinished="false"
					:reviewType="selectedReview.submissionDetails.uploadType"
				/>
				<p v-else>{{ $t('fbNoReviewYet') }}</p>
			</div>
		</div>
	</div>
</template>

<script>
import Table from '@/components/general/Table.vue';
import StudyInfo from '@/components/upload/StudyInfo.vue';
import ReviewSection from '@/components/review/ReviewSection.vue';
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
import { feedbackConfig } from '@/components/feedback/feedbackConfig.js';
import { feedbackCodebookTableConfig } from '@/components/feedback/feedbackCodebookTableConfig.js';
import { feedbackDataTableConfig } from '@/components/feedback/feedbackDataTableConfig';
import reviewModification from '@/assets/dummy/reviewModification.json';
import reviewAccepted from '@/assets/dummy/reviewAccepted.json';
import reviewDeclined from '@/assets/dummy/reviewDeclined.json';
import { ROUTE, REVIEW_STATUS, TOAST_TYPE, UPLOAD_TYP } from '@/enums/enums';

/**
 * @vuese
 * @group FeedbackView
 * Displays the feedback of a review by the maintainer for the user
 */
export default {
	name: 'FeedbackView',
	components: { Table, StudyInfo, ReviewSection, LoadingSpinner },
	emits: [],
	props: {},
	watch: {},
	setup() {},
	data() {
		return {
			isLoading: false,
			feedbackID: this.$route.params.feedbackID,
			feedbackConfig: feedbackConfig,
			selectedReview: null,
			reviewModification: reviewModification,
			reviewAccepted: reviewAccepted,
			reviewDeclined: reviewDeclined,
			selectedCodeBook: null,
			codebookTableConfig: feedbackCodebookTableConfig,
			dataTableConfig: feedbackDataTableConfig,
			codeBooksWithData: [],
			selectedItem: null,
		};
	},
	computed: {},
	created() {
		this.queryFeedback();
	},
	mounted() {},
	beforeDestroy() {},
	methods: {
		queryFeedback() {
			this.isLoading = true;

			this.$network.getData(`/api/review/feedback`, null, null, (err, data) => {
				try {
					if (!err) {
						this.feedbackConfig.data.values = data;
						this.selectedFeedbackWithID(this.feedbackID);
					} else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.isLoading = false;
					window.dispatchEvent(new Event('resize'));
				}
			});
		},
		selectedFeedbackWithID(feedbackID) {
			const selectedFeedback = this.feedbackConfig.data.values.find((review) => review.id === parseInt(feedbackID));
			if (selectedFeedback) {
				this.$nextTick(() => {
					this.selectReview(selectedFeedback);
				});
			} else {
				this.$global.showToast(TOAST_TYPE.ERROR, this.$t('fbFeedbackNotFound'));
				this.$router.go(-1);
			}
		},
		selectReview(review) {
			this.selectedReview = null;

			if (review) {
				this.isLoading = true;

				this.$router.push({ name: ROUTE.FEEDBACK_VIEW, params: { feedbackID: review.id } });
				this.feedbackID = review.id;
				this.$network.getData(`/api/review/feedback/${this.feedbackID}`, null, null, (err, data) => {
					try {
						if (!err) {
							this.selectedReview = data;
							this.setupCodeBooks();
						} else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
					} catch (error) {
						this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
					} finally {
						this.isLoading = false;
					}
				});
			}
		},
		setupCodeBooks() {
			this.selectedCodeBook = null;
			this.codeBooksWithData = [];

			// Assign the configuration based on uploadType
			const tableConfig = {
				[UPLOAD_TYP.UPLOAD_ONTOLOGY]: this.codebookTableConfig,
				[UPLOAD_TYP.UPLOAD_DATA]: this.dataTableConfig,
			}[this.selectedReview.submissionDetails.uploadType];

			// Set the title directly based on the uploadType
			this.uploadTypeTitle =
				this.selectedReview.submissionDetails.uploadType === UPLOAD_TYP.UPLOAD_ONTOLOGY
					? this.$t('fvUploadedCodebook')
					: this.selectedReview.submissionDetails.uploadType === UPLOAD_TYP.UPLOAD_DATA
						? this.$t('fvUploadedData')
						: '';

			// Helper function to create columns and rows
			const createColumnsAndRows = (data) => {
				const isStructuredData = Array.isArray(data[0]);
				const columns = isStructuredData
					? [
							{ ref: ['rowID'], text: this.$t('fvRowID') },
							...data[0].map((col) => ({
								ref: [col],
								text: col,
								formatter: (value) => {
									return this.$global.valueIsNotAvailable(value, true, false) ? '-' : value;
								},
							})),
						] // Structured data
					: [
							{ ref: ['rowID'], text: this.$t('fvRowID') },
							...data.map((col) => ({
								ref: [col.name],
								text: col.name,
								formatter: (value) => {
									return this.$global.valueIsNotAvailable(value, true, false) ? '-' : value;
								},
							})),
						]; // Non-structured data

				const rows = isStructuredData
					? data.slice(1).map((row, idx) => ({
							rowID: idx + 1,
							...row.reduce(
								(acc, val, i) => ({
									...acc,
									[data[0][i]]: this.$global.valueIsNotAvailable(val, true) ? '-' : val,
								}),
								{}
							),
						}))
					: data[0].rows.map((_, idx) => {
							const rowData = data.reduce(
								(acc, col) => ({
									...acc,
									[col.name]: this.$global.valueIsNotAvailable(col.rows[idx], true) ? '-' : col.rows[idx],
								}),
								{}
							);
							return { rowID: idx + 1, ...rowData };
						});

				return { columns, rows };
			};

			// Generate codeBooks with the appropriate configuration
			this.codeBooksWithData = this.selectedReview.submissionDetails.codeBooks.map((codeBook) => {
				const { columns, rows } = createColumnsAndRows(codeBook.data);
				return {
					id: codeBook.id,
					name: codeBook.name,
					tableConfig: {
						...tableConfig,
						data: { key: 'rowID', columns, values: rows },
					},
				};
			});

			// Set the first codeBook as the selected one
			this.selectedCodeBook = this.codeBooksWithData[0];
		},
		selectCodeBook(id) {
			this.selectedCodeBook = this.codeBooksWithData.find((it) => it.id == id);
		},
		selectItem(item) {
			this.selectedItem = item;
		},
	},
};
</script>

<style scoped>
.fv-wrap-content {
	width: 100%;
	position: relative;
	margin-bottom: 20px;
}
.fv-wrap-content h2 {
	margin: 10px 0px 20px 0px;
	text-decoration: underline;
	font-weight: normal;
}
.fv-wrap-submissions {
	margin: 10px 0px;
	padding: 2px;
	position: relative;
	overflow: hidden;
}
.fv-wrap-submission-details {
	width: 100%;
	padding: 10px 0px 20px 0px;
}
.fv-wrap-review-section {
	width: 100%;
	display: flex;
	justify-content: center;
	align-items: stretch;
	flex-flow: wrap;
	padding-top: 20px;
	gap: 0px 20px;
}
.fv-place-holder {
	flex: 1 1 calc(100% - 520px);
	min-width: 600px;
}
.fv-review-section {
	flex: 1 1 100%;
	min-width: 300px;
	margin-left: auto;
}

.fv-review-section p {
	width: 100%;
	margin: 20px 0px;
	font-size: 20px;
	text-align: center;
}
.fv-wrap-data-table {
	width: 100%;
}
.fv-tab-view {
	width: 100%;
	margin: 10px 0px 0px 0px;
	display: flex;
	justify-content: flex-start;
	align-items: flex-start;
	gap: 5px;
}
.fv-tab {
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
.fv-tab:hover {
	cursor: pointer;
	background-color: var(--main-color-5);
}
.fv-current-tab {
	background-color: var(--main-color-5);
}
</style>
