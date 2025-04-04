<template>
	<div class="le-wrap-content">
		<div :class="['le-element', legendClass]"></div>
		<div class="le-description">{{ text }}</div>
	</div>
</template>

<script>
/**
 * @vuese
 * @group Ontology
 * Legend element of the ontology header
 */
export default {
	name: 'LegendElement',
	components: {},
	emits: [],
	props: {
		text: {
			type: String,
			required: true,
		},
		legendClass: {
			type: String,
			required: true,
		},
	},
	watch: {},
	setup() {
		return {};
	},
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
.le-wrap-content {
	flex: 1 1 100%;
	margin: 10px;
	display: flex;
	justify-content: flex-start;
	align-items: center;
	gap: 10px;
}

.le-element {
	width: 20px;
	height: 20px;
	border-radius: 10px;
	border: 1px solid var(--main-color-dark);
}

.le-description {
	font-size: 16px;
}

.le-node {
	background-color: var(--main-color-node);
}

.le-leaf {
	background-color: var(--main-color-leaf);
}

.le-stakeholder {
	background-color: var(--main-color-stakeholder);
}

.le-data {
	background-color: var(--main-color-data);
}

.le-relationship {
	background-color: var(--main-color-relationship);
}

.le-added {
	background-color: var(--main-color-success);
}

.le-deleted {
	background-color: var(--main-color-error);
}

.le-modified {
	background-color: var(--main-color-warn);
}
</style>
