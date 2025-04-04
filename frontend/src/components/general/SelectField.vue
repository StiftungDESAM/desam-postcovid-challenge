<template>
	<div class="sf-wrap-content">
		<label :for="id">{{ labelText }}</label>
		<select
			:id="id"
			:disabled="disabled"
			@input="$emit('update:modelValue', $event.target.options[$event.target.selectedIndex].value)"
			@change="$emit('newValue', $event.target.options[$event.target.selectedIndex].value)"
		>
			<option :value="null" default selected hidden>{{ placeholder }}</option>
			<option v-for="opt in options" :key="opt" :value="opt" :selected="opt == modelValue">{{ $t(opt) }}</option>
		</select>
	</div>
</template>

<script>
import * as uuid from 'uuid';
/**
 * @vuese
 * @group General
 * Provides a selection field
 */
export default {
	name: 'SelectField',
	components: {},
	emits: ['newValue', 'update:modelValue'],
	props: {
		modelValue: {
			required: false,
			default: null,
		},
		labelText: {
			type: String,
			required: true,
		},
		placeholder: {
			type: String,
		},
		options: {
			type: Array,
			required: true,
		},
		disabled: {
			type: Boolean,
			default: false,
		},
	},
	watch: {},
	setup() {
		return {};
	},
	data() {
		return {
			id: uuid.v4().substring(0, 8),
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
.sf-wrap-content {
	flex: 1 1 200px;
	margin: 5px;
	box-sizing: border-box;
}

.sf-wrap-content label {
	margin: 5px;
	display: block;
}

.sf-wrap-content select {
	min-width: 200px;
	width: 100%;
	height: 40px;
}
</style>
