<template>
	<div class="if-wrap-content">
		<div v-if="inputType === 'checkbox'" class="if-wrap-checkbox-input">
			<label :for="id" :class="['if-custom-checkbox', disabled ? 'if-disabled-chedkbox' : null]">
				<input
					type="checkbox"
					:id="id"
					:checked="modelValue"
					:disabled="disabled"
					@input="$emit('update:modelValue', $event.target.checked)"
					@change="$emit('newValue', $event.target.checked)"
				/>
				<span class="if-checkmark"> <fai icon="fas fa-check"></fai> </span>
				<span v-if="labelText">{{ labelText }}</span>
			</label>
		</div>
		<div v-else-if="inputType == 'password'" class="if-wrap-password-input">
			<label v-if="labelText" :for="id">{{ labelText }}</label>
			<fai v-if="!showPassword" icon="fas fa-eye" @click="showPassword = true" />
			<fai v-else icon="fas fa-eye-slash" @click="showPassword = false" />
			<input
				:id="id"
				:type="showPassword ? 'text' : 'password'"
				:placeholder="placeholder"
				:autocomplete="autocompleteType"
				:value="modelValue"
				@focus="$emit('focus')"
				@blur="$emit('blur')"
				@input="$emit('update:modelValue', $event.target.value)"
				@change="$emit('newValue', $event.target.value)"
			/>
		</div>
		<div v-else-if="inputType == 'description'" class="if-wrap-description-input">
			<label :for="id">{{ labelText }}</label>
			<textarea
				:id="id"
				:placeholder="placeholder"
				:value="modelValue"
				:disabled="disabled"
				@input="$emit('update:modelValue', $event.target.value)"
				@change="$emit('newValue', $event.target.value)"
			/>
		</div>
		<div v-else class="if-wrap-all-input">
			<label :for="id">{{ labelText }}</label>
			<input
				:type="inputType"
				:id="id"
				:placeholder="placeholder"
				:value="modelValue"
				:disabled="disabled"
				@input="$emit('update:modelValue', $event.target.value)"
				@change="$emit('newValue', $event.target.value)"
			/>
		</div>
	</div>
</template>

<script>
import * as uuid from 'uuid';
/**
 * @vuese
 * @group General
 * Provides an Input field with description
 */
export default {
	name: 'InputField',
	components: {},
	emits: ['newValue', 'update:modelValue', 'focus', 'blur'],
	props: {
		modelValue: {
			required: false,
			default: null,
		},
		inputType: {
			type: String,
			default: 'text',
		},
		autocompleteType: {
			type: String,
			default: 'on',
		},
		placeholder: {
			type: String,
		},
		labelText: {
			type: String,
		},
		disabled: {
			type: Boolean,
			default: false,
		},
	},
	setup() {
		return {};
	},
	data() {
		return {
			id: uuid.v4().substring(0, 8),
			showPassword: false,
		};
	},
	computed: {},
	mounted() {},
	beforeDestroy() {},
	methods: {},
};
</script>

<style scoped>
.if-wrap-content {
	flex: 1 1 200px;
	margin: 5px;
	display: flex;
	align-items: stretch;
	flex-flow: column;
	box-sizing: border-box;
}

.if-wrap-all-input,
.if-wrap-password-input,
.if-wrap-description-input {
	position: relative;
}

.if-wrap-password-input svg {
	position: absolute;
	right: 7px;
	bottom: 12px;
	cursor: pointer;
}

.if-wrap-password-input label,
.if-wrap-all-input label,
.if-wrap-description-input label {
	margin: 5px;
	display: block;
}

.if-wrap-password-input input,
.if-wrap-all-input input,
.if-wrap-description-input input {
	min-width: 200px;
	width: 100%;
	height: 40px;
}

.if-wrap-password-input input {
	padding-right: 30px;
}

.if-wrap-description-input {
	flex: 1 1 100%;
	display: flex;
	align-items: stretch;
	flex-flow: column;
}

.if-wrap-description-input textarea {
	width: 100%;
	height: 100%;
	min-height: 120px;
	padding: 10px;
	font-size: 15px;
	resize: none;
}

.if-wrap-checkbox-input {
	display: flex;
	justify-content: flex-start;
	align-items: center;
}

.if-custom-checkbox {
	display: flex;
	justify-content: flex-start;
	align-items: center;
	flex-flow: wrap;
	gap: 10px;
	cursor: pointer;
	user-select: none;
}

.if-custom-checkbox input {
	display: none;
}

.if-disabled-chedkbox {
	cursor: default;
}

.if-disabled-chedkbox .if-checkmark {
	border: 2px solid var(--main-color-disabled) !important;
}

.if-checkmark {
	width: 15px;
	height: 15px;
	display: inline-flex;
	align-items: center;
	justify-content: center;
	border: 2px solid var(--main-color-light);
	border-radius: 5px;
	transition:
		background 0.3s,
		border-color 0.3s;
}

.if-checkmark ::v-deep(svg) * {
	font-size: 20px;
	opacity: 0;
	color: var(--main-color-5);
	transition: opacity 0.2s;
}

.if-custom-checkbox input:checked + .if-checkmark {
	background-color: var(--main-color-dark);
	border: 2px solid var(--main-color-4);
}

.if-custom-checkbox input:checked + .if-checkmark ::v-deep(svg) * {
	opacity: 1;
}
</style>
