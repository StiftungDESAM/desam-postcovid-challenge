<template>
	<div class="ma-wrap-content">
		<div class="ma-wrap-container">
			<h2>{{ $t('maMetaAssignmentDescription', { codeBook: codeBook.name }) }}</h2>
			<em>{{ $t('maAssignmentSelectionExplanationView') }}</em>

			<div v-if="codeBook.tableConfig">
				<div v-for="(header, index) in filteredHeaders" :key="header.ref" class="ma-wrap-check">
					<div class="ma-wrap-row">
						<div class="ma-check-header">
							<p>{{ header.text }}</p>
							(<InputField
								v-model="sharedKeys[index]"
								:labelText="$t('maMarkAsFieldName')"
								:inputType="'checkbox'"
								@newValue="toggleFieldNameCheckbox(index)"
							/>)
						</div>

						<div class="ma-check-select">
							<select
								v-model="header.selectedMeta"
								@change="onMetaChange(header)"
								:disabled="isFieldNameSelected(header)"
								:class="{
									'valid-selection': header.selectedMeta && header.selectedMeta !== 'REMOVE',
								}"
							>
								<option value="" disabled hidden>{{ $t('maNoMetaSelected') }}</option>
								<option value="REMOVE">{{ $t('maRemoveMetafieldSelection') }}</option>
								<option value="NEW">{{ $t('maNewMetafield') }}</option>
								<option v-for="meta in availableMetaFields(index)" :key="meta.tag" :value="meta.tag" :disabled="meta.disabled">
									{{ meta.name }}
									<span v-if="meta.assignedMetaField">({{ meta.assignedMetaField.name }})</span>
								</option>

								<option v-if="isFieldNameSelected(header)" :value="fieldNameMeta.tag" selected disabled>
									{{ fieldNameMeta.name }}
								</option>
							</select>
						</div>
					</div>
				</div>
			</div>

			<div class="ma-wrap-buttons" v-if="codeBook.tableConfig">
				<button class="app-default-btn" @click="resetToOriginalState">{{ $t('maCancel') }}</button>
				<button
					:class="metaFieldSelectionCompleted ? 'app-success-btn' : 'app-disabled-btn'"
					@click="assigneMetadata"
					:disabled="!metaFieldSelectionCompleted"
				>
					{{ $t('maAssigne') }}
				</button>
			</div>
		</div>
	</div>
</template>

<script>
import InputField from '@/components/general/InputField.vue';
/**
 * @vuese
 * @group Upload
 * Enables users to map codebook headers to existing metadata or set them to null to signal the creation of new metadata
 */
export default {
	name: 'MetaAssignment',
	emits: ['close', 'updateMetaAssignment'],
	components: { InputField },
	props: {
		codeBook: {
			type: Object,
			required: true,
		},
		metaAssignmentData: {
			type: Array,
			required: true,
		},
	},
	data() {
		return {
			originalMetaState: [],
			selectedFieldNameIndex: null,
			fieldNameMeta: null,
			sharedKeys: {},
		};
	},
	computed: {
		filteredHeaders() {
			return this.codeBook.tableConfig?.data?.columns?.filter((col) => col.ignoreFunctions !== true) || [];
		},
		metaFieldSelectionCompleted() {
			const allFieldsAssigned = this.filteredHeaders.every((header) => header.selectedMeta !== '' && header.selectedMeta !== 'REMOVE');
			const fieldNameAssigned = this.selectedFieldNameIndex !== null;
			return allFieldsAssigned && fieldNameAssigned;
		},
	},
	created() {
		this.initializeMetaSelection();
	},
	methods: {
		// Sets undefined or null selectedMeta to an empty string and saves the initial state
		initializeMetaSelection() {
			const fieldName = this.metaAssignmentData.find((meta) => meta.tag === 'Feldname');
			this.fieldNameMeta = fieldName || { name: 'Feldname', tag: 'Feldname' };

			// -1 because the first row is rowID and will be ignored
			this.codeBook.tableConfig?.data?.columns?.forEach((header, idx) => {
				if (header.ref.join('') !== 'rowID') {
					if (header.selectedMeta === undefined || header.selectedMeta === null) header.selectedMeta = '';
					if (header.selectedMeta == 'Feldname') {
						this.sharedKeys[idx - 1] = true;
						this.selectedFieldNameIndex = idx - 1;
						this.filteredHeaders[idx - 1].selectedMeta = this.fieldNameMeta.tag;
					} else this.sharedKeys[idx - 1] = false;
				}
			});
			this.saveOriginalMetaState();
		},
		saveOriginalMetaState() {
			this.originalMetaState = this.filteredHeaders.map((header) => ({
				ref: header.ref,
				selectedMeta: header.selectedMeta,
			}));
		},
		resetToOriginalState() {
			this.filteredHeaders.forEach((header) => {
				const original = this.originalMetaState.find((state) => state.ref === header.ref);
				if (original) {
					header.selectedMeta = original.selectedMeta;
				}
			});
			this.selectedFieldNameIndex = null;
			this.$emit('close');
		},
		onMetaChange(header) {
			if (header.selectedMeta === 'REMOVE') header.selectedMeta = '';
		},
		assigneMetadata() {
			const assignments = this.filteredHeaders.map((header, id) => ({
				id: id,
				header: header.text,
				metaDataItemTag: header.selectedMeta === 'NEW' ? null : header.selectedMeta,
			}));
			if (this.metaFieldSelectionCompleted) {
				this.$emit('updateMetaAssignment', assignments);
				this.$emit('close');
			}
		},
		resetMetaAssignment() {
			this.filteredHeaders.forEach((header) => (header.selectedMeta = ''));
			this.selectedFieldNameIndex = null;
			this.$emit('close');
		},
		isMetaAssigned(metaTAG) {
			return this.filteredHeaders.some((header) => header.selectedMeta === metaTAG);
		},
		toggleFieldNameCheckbox(index) {
			if (this.selectedFieldNameIndex === index) {
				this.filteredHeaders[index].selectedMeta = '';
				this.selectedFieldNameIndex = null;
			} else {
				if (this.selectedFieldNameIndex !== null) {
					this.filteredHeaders[this.selectedFieldNameIndex].selectedMeta = '';
				}
				this.selectedFieldNameIndex = index;
				this.filteredHeaders[index].selectedMeta = this.fieldNameMeta.tag;
			}

			// Reset all other inputs
			Object.keys(this.sharedKeys).forEach((key) => {
				if (key != index) this.sharedKeys[key] = false;
			});
		},
		isFieldNameSelected(header) {
			return this.selectedFieldNameIndex !== null && this.filteredHeaders[this.selectedFieldNameIndex] === header;
		},
		availableMetaFields(currentIndex) {
			const fieldNameTag = this.fieldNameMeta?.tag;
			return this.metaAssignmentData
				.map((meta) => {
					if (meta.tag === fieldNameTag && this.selectedFieldNameIndex !== currentIndex) {
						return null;
					}

					if (meta.tag === 'VerknuepftesItemID') {
						return null;
					}

					const isAssigned = this.isMetaAssigned(meta.tag);
					return {
						...meta,
						disabled: isAssigned && meta.tag !== this.filteredHeaders[currentIndex].selectedMeta,
					};
				})
				.filter((meta) => meta !== null);
		},
	},
};
</script>

<style scoped>
.ma-wrap-content {
	max-width: 80vw;
	max-height: 80vh;
	width: 1000px;
	border: 2px solid var(--main-color-light);
	border-radius: 10px;
	overflow-y: auto;
	overflow-x: hidden;
	box-sizing: border-box;
	position: relative;
	padding: 10px;
	background-color: var(--main-color-1);
}

.ma-wrap-content h2 {
	margin: 10px 0 15px 0;
	text-align: center;
}

.ma-wrap-container {
	padding: 0 15px;
}

.ma-wrap-container em {
	max-width: 500px;
	font-size: 20px;
}

.ma-wrap-row {
	width: 100%;
	margin: 15px 0px;
	display: flex;
	align-items: flex-start;
	justify-content: center;
	flex-flow: column;
}

.ma-check-header {
	flex: 1 1 100%;
	display: flex;
	justify-content: flex-start;
	align-items: center;
	flex-flow: row;
}

.ma-check-header p {
	min-width: fit-content;
	margin-right: 10px;
	text-decoration: un;
}

.ma-check-select {
	flex: 1 1 100%;
	width: 100%;
}

.ma-check-select select {
	width: 100%;
	margin-top: 5px;
	padding: 5px 10px;
	display: block;
	font-size: 18px;
	background-color: var(--main-color-5);
	color: var(--main-color-dark);
}

.ma-check-select select option {
	color: var(--main-color-dark);
}

.ma-check-select select.valid-selection {
	background-color: var(--main-color-2);
	color: var(--main-color-light);
}

.ma-check-select select.valid-selection:disabled {
	background-color: var(--main-color-dark-50);
}

.ma-wrap-buttons {
	width: 100%;
	display: flex;
	justify-content: center;
	gap: 5px 10px;
	text-align: center;
	padding: 10px 0;
}

.ma-wrap-buttons button {
	min-width: 200px;
	padding: 5px 10px;
	font-size: 18px;
}

.ma-wrap-checkbox {
	margin-top: 5px;
	display: flex;
	align-items: center;
	gap: 10px;
	font-weight: bold;
}
</style>
