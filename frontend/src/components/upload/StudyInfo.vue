<template>
	<div class="si-wrap-content">
		<div class="si-wrap-inputs">
			<InputField
				v-model="info.name"
				:placeholder="$t('ouStudyName')"
				:labelText="$t('ouStudyName')"
				:inputType="'text'"
				:disabled="disabled"
				@newValue="$emit('newStudyInfo', info)"
			/>
			<SelectField
				v-model="info.purpose"
				:placeholder="$t('ouStudyPurpos')"
				:labelText="$t('ouStudyPurpos')"
				:options="studyPurposeOptions"
				:disabled="disabled"
				@newValue="$emit('newStudyInfo', info)"
			/>
			<InputField
				v-model="info.dateStart"
				:labelText="$t('ouStudyDateStart')"
				:inputType="'date'"
				:disabled="disabled"
				@newValue="$emit('newStudyInfo', info)"
			/>
			<InputField
				v-model="info.dateEnd"
				:labelText="$t('reStudyDateEnd')"
				:inputType="'date'"
				:disabled="disabled"
				@newValue="$emit('newStudyInfo', info)"
			/>
			<InputField
				v-model="info.drksID"
				:placeholder="$t('ouStudyDrksId')"
				:labelText="$t('ouStudyDrksId')"
				:disabled="disabled"
				@newValue="$emit('newStudyInfo', info)"
			/>
		</div>
		<div class="si-wrap-textarea">
			<InputField
				v-model="info.description"
				:placeholder="$t('ouStudyDescription')"
				:labelText="$t('ouStudyDescription')"
				:inputType="'description'"
				:disabled="disabled"
				@newValue="$emit('newStudyInfo', info)"
			/>
		</div>
	</div>
</template>

<script>
import InputField from '@/components/general/InputField.vue';
import SelectField from '@/components/general/SelectField.vue';
import { STUDY_PURPOSE } from '@/enums/enums';
/**
 * @vuese
 * @group Upload
 * Info about the uploaded study
 */
export default {
	name: 'StudyInfo',
	components: { InputField, SelectField },
	emits: ['newStudyInfo'],
	props: {
		studyInfo: {
			type: Object,
			required: false,
		},
		disabled: {
			type: Boolean,
			required: false,
			default: false,
		},
	},
	watch: {},
	setup() {
		return {
			info: {},
		};
	},
	data() {
		return {
			studyPurposeOptions: Object.values(STUDY_PURPOSE),
		};
	},
	computed: {},
	created() {
		this.info = this.studyInfo;
	},
	mounted() {},
	beforeDestroy() {},
	methods: {},
};
</script>

<style scoped>
.si-wrap-content {
	width: 100%;
	min-height: 100px;
	display: flex;
	justify-content: flex-start;
	align-items: stretch;
	flex-flow: wrap;
	gap: 0px 20px;
}

.si-wrap-inputs {
	flex: 1 1 calc(100% - 820px);
	display: flex;
	justify-content: flex-start;
	align-items: stretch;
	flex-flow: wrap;
}

.si-wrap-inputs div {
	flex: 1 1 300px;
}

.si-wrap-textarea {
	flex: 1 1 800px;
	min-height: 150px;
	display: flex;
	justify-content: flex-start;
	align-items: stretch;
}
</style>
