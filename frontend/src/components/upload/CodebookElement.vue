<template>
	<div class="ce-wrap-content">
		<div v-if="row" class="ce-wrap-text">
			<h2>{{ $t('ceManuellQuestItemInfo') }} #{{ row['lineNumber'] }}</h2>
			<h3>{{ $t('ceTextInfo') }}</h3>
		</div>
		<div class="ce-wrap-item-table">
			<h3>{{ filteredLinkedData.length ? $t('ceAssignableItems') : $t('ceNoItemsAvailable') }}</h3>
			<table v-if="filteredLinkedData.length" class="ce-table-content">
				<thead>
					<tr>
						<th class="ce-table-header-item"></th>
						<th class="ce-table-header-item">#</th>
						<th v-for="(value, key) in filteredLinkedData[0]" :key="key" class="ce-table-header-item">
							{{ key === 'id' ? 'ID' : key }}
						</th>
					</tr>
				</thead>
				<tbody>
					<tr
						v-for="(item, index) in filteredLinkedData"
						:key="index"
						@click="handleCheckboxSelection(item, index)"
						:class="{ selected: selectedItem === index }"
					>
						<td class="ce-table-cell">
							<input
								type="checkbox"
								:checked="selectedItem === index"
								:value="index"
								@change="handleCheckboxSelection(item, index)"
								@click.stop
							/>
						</td>
						<td class="ce-table-cell">{{ index + 1 }}</td>
						<td v-for="(value, key) in item" :key="key" class="ce-table-cell">{{ value }}</td>
					</tr>
				</tbody>
			</table>
		</div>
		<div v-if="filteredLinkedData.length" class="ce-wrap-btn">
			<button class="app-warn-btn" @click="resetSelection">{{ $t('ceCancelSelection') }}</button>
			<button class="app-success-btn" @click="confirmSelection">
				{{ $t('ceConfirmSelection') }}
			</button>
		</div>
	</div>
</template>

<script>
/**
 * @vuese
 * @group Upload
 * Codebook element displayed in the Codebook table
 */
export default {
	name: 'CodebookElement',
	props: {
		row: Object,
		linkedData: Array,
	},
	data() {
		return {
			selectedItem: null,
			filteredLinkedData: [],
			selectedId: null,
		};
	},
	mounted() {
		this.filterLinkedData(this.linkedData, this.row);
	},
	watch: {
		linkedData(newLinkedData) {
			if (!newLinkedData || newLinkedData.length === 0) {
				this.filteredLinkedData = [];
				this.selectedItem = null;
				this.selectedId = null;
			} else {
				this.filterLinkedData(newLinkedData, this.row);
			}
		},
		row(newRow) {
			this.filterLinkedData(this.linkedData, newRow);
		},
	},
	methods: {
		filterLinkedData(linkedData, row) {
			const lineNumber = row['lineNumber'];

			// Filtering the linkedData by line number
			const filteredData = linkedData
				.filter((item) => Number(item.lineNumber) === Number(lineNumber))
				.map((item) => {
					return item.assignedItems.map((assignedItem) => ({
						...assignedItem,
					}));
				})
				.flat();

			this.filteredLinkedData = filteredData;

			if (row.assignedItemID) {
				// Find the item in linkedData using the 'assignedItemID'
				const selectedItem = this.filteredLinkedData.find((item) => item.id === row.assignedItemID);
				this.selectedItem = this.filteredLinkedData.indexOf(selectedItem);
				this.selectedId = selectedItem.id;
			} else {
				this.selectedItem = null;
				this.selectedId = null;
			}
		},
		handleCheckboxSelection(item, index) {
			this.selectedItem = this.selectedItem === index ? null : index;
			this.selectedId = this.selectedItem !== null ? item.id : null;
		},
		resetSelection() {
			this.$emit('updateAssignedItem', { ...this.row, assignedItemID: null });
		},
		confirmSelection() {
			if (this.selectedId !== null && this.selectedId !== undefined) {
				if (this.selectedId !== this.row.assignedItemID) {
					this.$emit('updateAssignedItem', {
						...this.row,
						assignedItemID: this.selectedId,
					});
				} else {
					this.$emit('updateAssignedItem', {
						...this.row,
						assignedItemID: this.row.assignedItemID,
					});
				}
			} else {
				this.$emit('updateAssignedItem', {
					...this.row,
					assignedItemID: null,
				});
			}
		},
	},
};
</script>

<style scoped>
.ce-wrap-item-table {
	width: 100%;
	overflow: auto;
}

.ce-wrap-text h2 {
	margin: 20px 0 10px 0;
	padding: 1px;
	font-weight: normal;
}

.ce-wrap-text h3 {
	margin: 10px 0 20px 0;
	padding: 1px;
	font-weight: normal;
	text-align: justify;
	word-wrap: break-word;
}

.ce-table-content {
	width: 100%;
	margin-top: 20px;
	border-collapse: collapse;
	table-layout: auto;
	background-color: var(--main-color-4);
	border: 1px solid var(--main-color-light);
}

.ce-table-header-item,
.ce-table-cell {
	text-align: left;
	word-wrap: break-word;
	white-space: nowrap;
}

.ce-table-header-item {
	height: 30px;
	padding: 10px;
	font-weight: bold;
	background-color: var(--main-color-dark);
	color: var(--main-color-light);
	border-bottom: 1px solid var(--main-color-light);
}

.ce-table-cell {
	padding: 15px 10px;
	color: var(--main-color-dark);
	border-bottom: 1px solid var(--main-color-dark);
	border-right: 1px solid var(--main-color-dark);
}

.ce-table-content tr:hover,
.ce-table-content tr.selected {
	background-color: var(--main-color-5) !important;
	cursor: pointer;
}

.ce-wrap-btn {
	width: 100%;
	text-align: center;
	display: flex;
	justify-content: flex-end;
	margin-top: 15px;
}

.ce-wrap-btn button {
	min-width: 200px;
	height: 40px;
	margin: 5px;
	font-size: 16px;
}

.cancel-button {
	background-color: var(--main-color-light);
	color: var(--main-color-dark);
}

.cancel-button:hover {
	background-color: var(--main-color-5);
}
</style>
