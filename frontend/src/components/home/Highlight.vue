<template>
	<div class="hl-wrap-content">
		<h3>{{ study.name }}</h3>
		<div class="hl-wrap-figures">
			<div class="hl-figure">
				<p>{{ $t('hiQuestionnaires') }}</p>
				<span>{{ study.questionnaires }}</span>
			</div>
			<div class="hl-figure">
				<p>{{ $t('hiQuestions') }}</p>
				<span>{{ study.questions }}</span>
			</div>
			<div class="hl-figure">
				<p>{{ $t('hiParticipants') }}</p>
				<span>{{ study.participants }}</span>
			</div>
			<div class="hl-figure">
				<p>{{ $t('hiDataPoints') }}</p>
				<span>{{ study.datapoints }}</span>
			</div>
		</div>
	</div>
</template>

<script>
/**
 * @vuese
 * @group Home
 * Highlights a certain study
 */
export default {
	name: 'Highlight',
	components: {},
	emits: [],
	props: {
		study: {
			type: Object,
			required: true,
		},
	},
	watch: {},
	data() {
		return {};
	},
	computed: {},
	created() {},
	mounted() {},
	beforeDestroy() {},
	methods: {},
};
</script>

<style scoped>
.hl-wrap-content {
	flex: 1 1 200px;
	min-width: fit-content;
	min-height: 100px;
	margin: 10px 20px;
	padding: 10px;
	border: 1px solid var(--main-color-dark);
	border-radius: 5px;
	background-color: var(--main-color-4);
}

.hl-wrap-content h3 {
	text-decoration: underline;
	color: var(--main-color-dark);
}

.hl-wrap-figures {
	width: 100%;
	margin: 10px 0px;
}

.hl-figure {
	width: 100%;
	padding: 10px 0px;
}

.hl-figure p {
	display: inline;
	color: var(--main-color-dark);
}

.hl-figure span {
	display: inline;
	float: right;
	color: var(--main-color-dark);
}
</style>
