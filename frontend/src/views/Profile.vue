<template>
	<div class="pr-wrap-content">
		<h2>{{ $t('prSubmittedStudies') }}</h2>
		<div class="pr-wrap-studies-table">
			<LoadingSpinner v-if="isLoading" :wrapperClass="'pr-wrap-studies-table'" />
			<Table :config="submissionsConfig" @selectItem="selectItem" />
		</div>
	</div>
</template>

<script>
import Table from '@/components/general/Table.vue';
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
import { submissionsConfig } from '@/components/user/submissionsConfig';
import submissions from '@/assets/dummy/allSubmissions.json';
import { ROUTE, TOAST_TYPE } from '@/enums/enums';

/**
 * @vuese
 * @group Profile
 * Displays the profile of a user with link to feedback view of ontology and data reviews
 */
export default {
	name: 'Profile',
	components: { Table, LoadingSpinner },
	emits: [],
	props: {},
	watch: {},
	setup() {
		return { ROUTE };
	},
	data() {
		return {
			isLoading: false,
			submissions: submissions,
			submissionsConfig: submissionsConfig,
			selectedItem: null,
		};
	},
	computed: {},
	created() {
		this.querySubmissions();
	},
	mounted() {},
	beforeDestroy() {},
	methods: {
		querySubmissions() {
			this.isLoading = true;

			window.setTimeout(() => {
				this.$network.getData(`/api/profile/submissions`, null, null, (err, data) => {
					try {
						// TODO: Remove mocked data
						// if (!err) this.tableConfig.data.values = data;
						if (err) this.submissionsConfig.data.values = this.submissions;
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
		selectItem(item) {
			// Check whether the status is not 'OPEN' or 'ASSIGNED'
			if (['OPEN', 'ASSIGNED'].includes(item.submissionStatus)) {
				// display warn because no feedback exists
				this.$global.showToast(TOAST_TYPE.WARN, this.$t('pfFeedbackNotAvailable'));
			} else {
				// if feedback exists forwarding to the FeedbackView with feedbackID
				this.$router.push({ name: ROUTE.FEEDBACK_VIEW, params: { feedbackID: item.id } });
			}
		},
	},
};
</script>

<style scoped>
.pr-wrap-content {
	width: 100%;
	position: relative;
}

.pr-wrap-content h2 {
	margin: 10px 0px 20px 0px;
	text-decoration: underline;
	font-weight: normal;
}

.pr-wrap-studies-table {
	margin: 10px 0px;
	padding: 2px;
	position: relative;
	overflow: hidden;
	padding-bottom: 10px;
}
</style>
