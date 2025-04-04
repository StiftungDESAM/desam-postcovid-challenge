<template>
	<div class="cw-wrap-content" @click.stop="config.cancelButton.callback">
		<div @click.stop="" class="cw-wrap-window">
			<div class="cw-wrap-text">
				<h2>{{ config.title }}</h2>
				<p>{{ config.text }}</p>
			</div>
			<div class="cw-wrap-buttons">
				<button :class="config.cancelButton.class" @click.stop="config.cancelButton.callback">{{ config.cancelButton.text }}</button>
				<button :class="config.confirmButton.class" @click.stop="config.confirmButton.callback">{{ config.confirmButton.text }}</button>
			</div>
		</div>
	</div>
</template>

<script>
/**
 * @vuese
 * @group General
 * Confirmation window for a certain action
 *
 * Config structure:
 *
 * {
 * 		title: String, // Title of the confirmation window
 * 		text: String, // Text of the confirmation window
 * 		cancelButton: { // The button that cancels the action
 * 			class: String, // The class of the button
 * 			text: String, // The text of the button
 * 			callback: Function // Function that gets called on click
 * 		},
 * 		confirmButton: { // The button that confirms the action
 * 			class: String, // The class of the button
 * 			text: String, // The text of the button
 * 			callback: Function // Function that gets called on click
 * 		}
 * }
 */
export default {
	name: 'ConfirmationWindow',
	components: {},
	emits: [],
	props: {
		config: {
			type: Object,
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
.cw-wrap-content {
	width: 100%;
	height: 100%;
	position: fixed;
	top: 0px;
	left: 0px;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: column;
	z-index: 2;
	background-color: var(--main-color-dark-bb);
}

.cw-wrap-window {
	max-width: 50%;
	max-height: 80%;
	padding: 20px;
	border: 1px solid var(--main-color-light);
	border-radius: 10px;
	overflow: auto;
	background-color: var(--main-color-1);
}

.cw-wrap-text {
	width: 100%;
	text-align: center;
}

.cw-wrap-text p {
	margin: 10px 0px 20px 0px;
}

.cw-wrap-buttons {
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: wrap;
}

.cw-wrap-buttons button {
	flex: 1 1 200px;
	min-width: 200px;
	max-width: 400px;
	margin: 2px 5px;
	padding: 10px 5px;
	font-size: 17px;
}
</style>
