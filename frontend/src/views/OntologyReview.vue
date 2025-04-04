<template>
	<div class="or-wrap-content">
		<h2>{{ $t('orSubmissions') }}</h2>
		<ConfirmationWindow v-if="confirmationConfig" :config="confirmationConfig" />
		<div class="or-wrap-submissions">
			<LoadingSpinner v-if="isLoading" :wrapperClass="'or-wrap-submissions'" />
			<Table :config="tableConfig" :resetSelected="resetSelected" @selectItem="selectReview" />
		</div>
		<div v-if="selectedReview" class="or-wrap-submission-details">
			<h2>{{ $t('orSubmissionDetails') }}</h2>
			<StudyInfo v-if="selectedReview.submissionDetails.studyInfo" :disabled="true" :studyInfo="selectedReview.submissionDetails.studyInfo" />
			<div v-else class="or-no-submission-details">{{ $t('orNoSubmissionDetails') }}</div>
		</div>
		<h2 v-if="selectedReview">{{ $t('orOntologyChanges') }}</h2>
		<div v-if="selectedReview" class="or-wrap-viewer">
			<OntologyViewer :rdfData="selectedReview.submissionDetails.modifiedOntology" :selectedElement="selectedElement" />
		</div>
		<div v-if="selectedReview" class="or-wrap-bottom">
			<div class="or-wrap-migrations">
				<h2>{{ $t('orMigrationOperations') }}</h2>
				<MigrationOperations :migrations="selectedReview.submissionDetails.migrationOperations" @highlightMigration="highlightMigration" />
			</div>
			<div class="or-wrap-review-section">
				<h2>{{ $t('orReviewSection') }}</h2>
				<ReviewSection
					:reviewID="selectedReview.id"
					:reviewer="selectedReview.reviewer"
					:reviewDetails="selectedReview.review"
					:userIsReviewerAndNotFinished="userIsReviewerAndNotFinished"
					@assignReview="assignReview"
					@updateReview="selectedReview.review = $event"
				/>
			</div>
		</div>
		<div v-if="selectedReview" class="or-wrap-buttons">
			<LoadingSpinner v-if="isUpdating" :positioning="'fixed'" />
			<button :class="userIsReviewerAndNotFinished ? 'app-default-btn' : 'app-disabled-btn'" @click="saveAsDraft()">
				{{ $t('orSaveAsDraft') }} <fai icon="fas fa-save" />
			</button>
			<button :class="userIsReviewerAndNotFinished ? 'app-default-btn' : 'app-disabled-btn'" @click="saveAsDraftAndClose">
				{{ $t('orSaveAsDraftAndClose') }} <fai icon="fas fa-save" />
			</button>
			<button :class="userIsReviewerAndNotFinished ? 'app-success-btn' : 'app-disabled-btn'" @click="confirmFinishReview">
				{{ $t('orFinishReview') }} <fai icon="fas fa-paper-plane" />
			</button>
		</div>
	</div>
</template>

<script>
import Table from '@/components/general/Table.vue';
import StudyInfo from '@/components/upload/StudyInfo.vue';
import OntologyViewer from '@/components/ontology/OntologyViewer.vue';
import ReviewSection from '@/components/review/ReviewSection.vue';
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
import MigrationOperations from '@/components/review/MigrationOperations.vue';
import ConfirmationWindow from '@/components/general/ConfirmationWindow.vue';
import ontologyReviews from '@/assets/dummy/ontologyReviews.json';
import openReview from '@/assets/dummy/openOntologyReview.json';
import assignedReview from '@/assets/dummy/assignedOntologyReview.json';
import closedReview from '@/assets/dummy/closedOntologyReview.json';
import modifiedOntology from '@/assets/dummy/modifiedOntology.json';
import { tableConfig } from '@/components/review/ontologyReviewTableConfig.js';
import { REVIEW_STATUS, TOAST_TYPE } from '@/enums/enums';
/**
 * @vuese
 * @group OntologyReview
 * Provides the maintainer with information about the uploaded ontology and review tools
 */
export default {
	name: 'OntologyReview',
	components: { OntologyViewer, Table, StudyInfo, ReviewSection, LoadingSpinner, MigrationOperations, ConfirmationWindow },
	emits: [],
	props: {},
	watch: {},
	setup() {
		return {};
	},
	data() {
		return {
			modifiedOntology: modifiedOntology.rdf,
			ontologyReviews: ontologyReviews,
			openReview: openReview,
			assignedReview: assignedReview,
			closedReview: closedReview,
			tableConfig: tableConfig,
			currentUser: this.$store.getCurrentUser(),
			selectedReview: null,
			isLoading: false,
			isUpdating: false,
			selectedElement: null,
			resetSelected: false,
			confirmationConfig: null,
		};
	},
	computed: {
		userIsReviewerAndNotFinished() {
			return (
				this.selectedReview?.reviewer?.email == this.currentUser.credentials.email &&
				this.selectedReview?.submissionStatus == REVIEW_STATUS.ASSIGNED
			);
		},
	},
	created() {
		this.queryReviews();
	},
	mounted() {},
	beforeDestroy() {},
	methods: {
		queryReviews() {
			this.isLoading = true;

			window.setTimeout(() => {
				this.$network.getData(`/api/review/ontology`, null, null, (err, data) => {
					try {
						// TODO: Remove mocked data
						// if (!err) this.tableConfig.data.values = data;
						if (err) this.tableConfig.data.values = this.ontologyReviews;
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
					this.$network.getData(`/api/review/ontology/${review.id}`, null, null, (err, data) => {
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
								this.selectedReview.submissionDetails.modifiedOntology = this.modifiedOntology;
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
		highlightMigration(migration) {
			if (migration) {
				window.scrollTo({
					top: document.querySelector('.or-wrap-viewer').offsetTop - 10,
					behavior: 'smooth',
				});
				this.selectedElement = migration.tag;
			} else this.selectedElement = null;
		},
		assignReview() {
			this.selectedReview.submissionStatus = REVIEW_STATUS.ASSIGNED;
			this.selectedReview.reviewer = {
				firstName: this.currentUser.user.firstName,
				lastName: this.currentUser.user.lastName,
				email: this.currentUser.credentials.email,
			};
		},
		saveAsDraft(cb) {
			this.updateReview({ submissionState: REVIEW_STATUS.ASSIGNED, review: this.selectedReview.review }, false, cb);
		},
		saveAsDraftAndClose() {
			this.saveAsDraft(() => {
				this.selectedReview = null;
				this.resetSelected = !this.resetSelected;
				this.queryReviews();
			});
		},
		confirmFinishReview() {
			this.confirmationConfig = {
				title: this.$t('orFinishReviewTitle'),
				text: this.$t('orFinishReviewText'),
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
				this.queryReviews();
			});
		},
		updateReview(update, isFinish, cb) {
			this.isUpdating = true;

			window.setTimeout(() => {
				this.$network.patchData(`/api/review/ontology/${this.selectedReview.id}`, update, null, (err, data) => {
					try {
						// TODO: Remove mocked data
						// if (!err) {
						if (err) {
							if (isFinish) this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('orFinishedSuccessfully'));
							else this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('orSavedSuccessfully'));
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
.or-wrap-content {
	width: 100%;
	position: relative;
	margin-bottom: 20px;
}

.or-wrap-content h2 {
	margin: 10px 0px 20px 0px;
	text-decoration: underline;
	font-weight: normal;
}

.or-wrap-submissions {
	margin: 10px 0px;
	padding: 2px;
	position: relative;
	overflow: hidden;
}

.or-wrap-submission-details {
	width: 100%;
	padding: 10px 0px 20px 0px;
}

.or-no-submission-details {
	width: 100%;
	padding: 0px 10%;
	font-size: 18px;
	box-sizing: border-box;
	text-align: center;
}

.or-wrap-viewer {
	width: 100%;
	height: 80vh;
	min-width: 500px;
	margin: 2px;
	position: relative;
	overflow: hidden;
	border: 1px solid var(--main-color-light);
	box-sizing: border-box;
}

.or-wrap-bottom {
	width: 100%;
	display: flex;
	justify-content: center;
	align-items: stretch;
	flex-flow: wrap;
	gap: 0px 20px;
}

.or-wrap-migrations {
	flex: 1 1 calc(100% - 520px);
	min-width: 600px;
}

.or-wrap-review-section {
	flex: 1 1 500px;
}

.or-wrap-buttons {
	width: 100%;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: wrap;
}

.or-wrap-buttons button {
	min-width: 250px;
	margin: 5px;
	padding: 10px 5px;
	font-size: 17px;
}
</style>
