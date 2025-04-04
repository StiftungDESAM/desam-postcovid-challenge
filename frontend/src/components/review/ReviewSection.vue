<template>
	<div class="rs-wrap-content">
		<ConfirmationWindow v-if="confirmationConfig" :config="confirmationConfig" />
		<div class="rs-wrap-reviewer">
			<p v-if="reviewer">
				<span>{{ $t('rsReviewer') }}: {{ reviewer.firstName }} {{ reviewer.lastName }}</span>
			</p>
			<p v-else>
				<span>{{ $t('rsNoReviewerAssigned') }}</span>
				<button class="app-success-btn" @click="confirmReviewAssignment">{{ $t('rsAssignYourself') }}</button>
			</p>
		</div>
		<div class="rs-wrap-review">
			<div class="rs-wrap-comment">
				<label>{{ $t('rsReviewComment') }}</label>
				<textarea v-model="reviewComment" :disabled="!userIsReviewerAndNotFinished" @change="updateReview"></textarea>
			</div>
			<div class="rs-wrap-status">
				<div class="rs-status">
					<input
						id="accepted"
						type="radio"
						:value="rsEnum.ACCEPTED"
						v-model="reviewStatus"
						:disabled="!userIsReviewerAndNotFinished"
						@click="handleRadioClick(rsEnum.ACCEPTED)"
					/>
					<label for="accepted">{{ $t('rsAccepted') }}</label>
				</div>
				<div class="rs-status">
					<input
						id="modification"
						type="radio"
						:value="rsEnum.MODIFICATION_NEEDED"
						v-model="reviewStatus"
						:disabled="!userIsReviewerAndNotFinished"
						@click="handleRadioClick(rsEnum.MODIFICATION_NEEDED)"
					/>
					<label for="modification">{{ $t('rsModificationNeeded') }}</label>
				</div>
				<div class="rs-status">
					<input
						id="declined"
						type="radio"
						:value="rsEnum.DECLINED"
						v-model="reviewStatus"
						:disabled="!userIsReviewerAndNotFinished"
						@click="handleRadioClick(rsEnum.DECLINED)"
					/>
					<label for="declined">{{ $t('rsDeclined') }}</label>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import ConfirmationWindow from '@/components/general/ConfirmationWindow.vue';
import { REVIEW_STATUS, TOAST_TYPE } from '@/enums/enums';
/**
 * @vuese
 * @group Review
 * Displays review components needed for reviewing the related submission
 */
export default {
	name: 'ReviewSection',
	components: { ConfirmationWindow },
	emits: ['assignReview', 'updateReview'],
	props: {
		reviewID: {
			type: Number,
			required: true,
		},
		reviewer: {
			type: Object,
			required: false,
		},
		reviewDetails: {
			type: Object,
			required: true,
		},
		userIsReviewerAndNotFinished: {
			type: Boolean,
			required: true,
		},
	},
	watch: {},
	setup() {
		const rsEnum = REVIEW_STATUS;

		return { rsEnum };
	},
	data() {
		return {
			currentUser: this.$store.getCurrentUser(),
			confirmationConfig: null,
			reviewComment: this.reviewDetails.comment,
			reviewStatus: this.reviewDetails.status,
		};
	},
	created() {},
	mounted() {},
	beforeDestroy() {},
	methods: {
		confirmReviewAssignment() {
			this.confirmationConfig = {
				title: this.$t('rsAssignReviewToYourselfTitle'),
				text: this.$t('rsAssignReviewToYourselfText'),
				cancelButton: {
					class: 'app-default-btn',
					text: this.$t('rsCancel'),
					callback: () => {
						this.confirmationConfig = null;
					},
				},
				confirmButton: {
					class: 'app-success-btn',
					text: this.$t('rsAssignYourself'),
					callback: () => {
						this.confirmationConfig = null;
						this.assignToReview();
					},
				},
			};
		},
		assignToReview() {
			this.isLoading = true;

			window.setTimeout(() => {
				this.$network.postData(
					`/api/review/ontology/${this.reviewID}/assign-to-review`,
					{ email: this.currentUser.credentials.email },
					null,
					(err, data) => {
						try {
							// TODO: Remove mocked data
							// if (!err) {
							// 	this.$emit('assignReview')
							// 	this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('rsAssignedReviewSuccessfully'))
							// }
							if (err) {
								this.$emit('assignReview');
								this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('rsAssignedReviewSuccessfully'));
							} else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
						} catch (error) {
							this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
						} finally {
							this.isLoading = false;
						}
					}
				);
			}, 1000);
		},
		handleRadioClick(status) {
			this.reviewStatus = this.reviewStatus === status ? null : status;
			this.updateReview();
		},
		updateReview() {
			this.$emit('updateReview', { status: this.reviewStatus, comment: this.reviewComment });
		},
	},
};
</script>

<style scoped>
.rs-wrap-content {
	width: 100%;
	height: calc(100% - 70px);
	padding-bottom: 10px;
	position: relative;
}

.rs-wrap-reviewer {
	width: 100%;
	padding-bottom: 10px;
}

.rs-wrap-reviewer p {
	width: 100%;
	margin: 0px;
	padding: 0px;
	font-size: 20px;
}

.rs-wrap-reviewer p span {
	padding: 0px 0px 10px 2px;
	display: block;
}

.rs-wrap-review {
	width: 100%;
}

.rs-wrap-comment {
	width: 100%;
	margin-bottom: 10px;
	display: flex;
	justify-content: center;
	align-items: flex-start;
	flex-flow: column;
}

.rs-wrap-comment label {
	padding: 0px 0px 5px 2px;
}

.rs-wrap-comment textarea {
	width: 100%;
	min-height: 150px;
	padding: 10px;
	box-sizing: border-box;
}

.rs-wrap-status {
	width: 100%;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: wrap;
}

.rs-status {
	flex: 1 1 100%;
	height: 15px;
	display: flex;
	justify-content: flex-start;
	align-items: center;
	padding: 5px 0px 5px 2px;
}

.rs-status input {
	margin-right: 10px;
}

.rs-status label {
	cursor: pointer;
}
</style>
