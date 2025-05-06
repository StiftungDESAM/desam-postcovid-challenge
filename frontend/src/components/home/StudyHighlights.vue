<template>
	<div class="sh-wrap-content">
		<h3>{{ highlight.name }}</h3>
		<div class="sh-wrap-figures">
			<div class="sh-figure">
				<p>{{ $t('shQuestionnaires') }}</p>
				<span>{{ highlight.questionnaires }}</span>
			</div>
			<div class="sh-figure">
				<p>{{ $t('shQuestions') }}</p>
				<span>{{ highlight.questions }}</span>
			</div>
			<div class="sh-figure">
				<p>{{ $t('shParticipants') }}</p>
				<span>{{ highlight.participants }}</span>
			</div>
			<div class="sh-figure">
				<p>{{ $t('shDataPoints') }}</p>
				<span>{{ highlight.datapoints }}</span>
			</div>
		</div>
	</div>
</template>

<script>
/**
 * @vuese
 * @group Home
 * Highlights uploaded studies in the system
 */
export default {
	name: 'StudyHighlights',
	components: {},
	emits: [],
	props: {
		highlight: {
			type: Object,
			required: true,
		},
	},
	watch: {},
	setup() {
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
.sh-wrap-content {
	flex: 1 1 200px;
	min-width: fit-content;
	min-height: 100px;
	margin: 10px 20px;
	padding: 10px;
	border: 1px solid var(--main-color-dark);
	border-radius: 5px;
	background-color: var(--main-color-4);
}

.sh-wrap-content h3 {
	text-decoration: underline;
	color: var(--main-color-dark);
}

.sh-wrap-figures {
	width: 100%;
	margin: 10px 0px;
}

.sh-figure {
	width: 100%;
	padding: 10px 0px;
}

.sh-figure p {
	display: inline;
	color: var(--main-color-dark);
}

.sh-figure span {
	display: inline;
	float: right;
	color: var(--main-color-dark);
}
</style>
