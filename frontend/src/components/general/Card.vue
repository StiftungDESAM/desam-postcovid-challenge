<template>
	<div :class="wrapperClass">
		<slot></slot>
	</div>
</template>

<script>
/**
 * @vuese
 * @group General
 * Card with basic style and slot for dynamic content
 */
export default {
	name: 'Card',
	components: {},
	emits: [],
	props: {
		cardType: {
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
	computed: {
		wrapperClass() {
			if (this.cardType === 'SQUARE') return 'ca-wrap-square';
			else if (this.cardType === 'RECTANGLE') return 'ca-wrap-rectangle';
			else return 'ca-wrap-square';
		},
	},
	created() {},
	mounted() {},
	beforeDestroy() {},
	methods: {},
};
</script>

<style scoped>
.ca-wrap-square {
	min-width: 200px;
	min-height: 200px;
	margin: 10px;
	padding: 10px;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: column;
	border-radius: 5px;
	box-shadow: -0px -0px 4px 4px var(--main-color-dark);
	box-sizing: border-box;
	aspect-ratio: 1;
	background-color: var(--main-color-2);
}

.ca-wrap-square * {
	color: var(--main-color-light);
}

.ca-wrap-square:hover {
	background-color: var(--main-color-3);
	cursor: pointer;
}

.ca-wrap-square:hover * {
	color: var(--main-color-dark);
}

/* v-deep ignores scope for a certain element. Needed to style content in slot from outside */
.ca-wrap-square ::v-deep(svg) {
	height: 60px;
	margin-bottom: 20px;
	filter: drop-shadow(4px 4px 1px var(--main-color-dark));
}

.ca-wrap-square:hover ::v-deep(svg) {
	filter: none;
}

.ca-wrap-square ::v-deep(p) {
	font-size: 20px;
}

.ca-wrap-rectangle {
	min-width: 200px;
	min-height: 50px;
	margin: 10px;
	padding: 20px;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: row;
	border-radius: 5px;
	box-shadow: -0px -0px 4px 4px var(--main-color-dark);
	box-sizing: border-box;
	background-color: var(--main-color-2);
}

.ca-wrap-rectangle * {
	color: var(--main-color-light);
}

.ca-wrap-rectangle:hover {
	background-color: var(--main-color-3);
	cursor: pointer;
}

.ca-wrap-rectangle:hover * {
	color: var(--main-color-dark);
}

/* v-deep ignores scope for a certain element. Needed to style content in slot from outside */
.ca-wrap-rectangle ::v-deep(svg) {
	height: 35px;
	margin-left: 10px;
	filter: drop-shadow(4px 4px 1px var(--main-color-dark));
}

.ca-wrap-rectangle:hover ::v-deep(svg) {
	filter: none;
}

.ca-wrap-rectangle ::v-deep(p) {
	font-size: 25px;
}
</style>
