<template>
	<div class="sh-wrap-content">
		<h2>{{ $t('shHighlightedStudies') }}:</h2>
		<div class="sh-wrap-highlights">
			<Highlight v-for="study in studies" :key="study.id" :study="study" />
		</div>
	</div>
</template>

<script>
import Highlight from './Highlight.vue';
import highlightedStudies from '@/assets/dummy/highlightedStudies.json';
/**
 * @vuese
 * @group Home
 * Highlights uploaded studies in the system
 */
export default {
	name: 'StudyHighlights',
	components: { Highlight },
	emits: [],
	props: {},
	watch: {},
	setup() {
		return {};
	},
	data() {
		return {
			// TODO: Replace mocked studies
			studies: highlightedStudies,
		};
	},
	computed: {},
	created() {},
	mounted() {},
	beforeDestroy() {},
	methods: {},
};
</script>

<style scoped>
.sh-wrap-content h2 {
	margin: 20px 0px 10px 10px;
	font-weight: normal;
}

.sh-wrap-highlights {
	display: flex;
	justify-content: center;
	flex-flow: wrap;
	box-sizing: border-box;
}
</style>
