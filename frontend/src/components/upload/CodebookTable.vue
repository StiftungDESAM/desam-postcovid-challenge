<template>
	<div class="ct-wrap-content">
		<h2 v-if="tables.length" class="ct-header-preview">{{ $t('ctHeaderPreview') }}</h2>
		<ConfirmationWindow v-if="confirmationDeletion" :config="confirmationDeletion" />
		<div class="ct-wrap-tabs">
			<ul class="ct-tab-list">
				<li v-for="(table, index) in tables" :key="index" :class="{ 'ct-tab-active': activeTab === index }" @click="changeTab(index)">
					{{ table.fileName }}
					<fai icon="fas fa-times" title="Cancel" @click.stop="deleteTable(index)" />
				</li>
			</ul>
			<div class="ct-tab-content">
				<table v-if="currentTable" class="ct-table-content">
					<thead>
						<tr class="ct-table-header">
							<!-- First two headers empty -->
							<th class="ct-table-header-item"></th>
							<th class="ct-table-header-item">#</th>
							<th
								v-for="(header, index) in currentTable.columns"
								:key="index"
								class="ct-table-header-item"
								:style="{ minWidth: calculateWidth(header), maxWidth: calculateWidth(header, true) }"
							>
								<div class="ct-header-actions">
									<span v-if="editingHeader !== index" class="ct-header-text">{{ header }}</span>
									<input
										v-if="editingHeader === index"
										v-model="newHeaderValue"
										class="ct-header-input"
										type="text"
										@keyup.enter="saveColumn(index)"
									/>
									<div class="ct-header-icons">
										<fai
											v-if="editingHeader !== index"
											icon="fas fa-pen"
											title="Edit"
											class="ct-header-icon"
											@click="editColumn(index)"
										/>
										<fai v-if="editingHeader === index" icon="fas fa-times" title="Cancel" @click="cancelEdit" />
										<fai
											v-if="editingHeader === index && newHeaderValue !== currentTable.columns[index]"
											icon="fas fa-floppy-disk"
											title="Save"
											@click="saveColumn(index)"
										/>
										<fai
											v-if="editingHeader !== index"
											icon="fas fa-trash"
											title="Delete"
											@click="confirmDeletion(deleteColumn, index, 'column')"
										/>
									</div>
								</div>
							</th>
						</tr>
					</thead>
					<tbody class="ct-table-body" @dragover.prevent="onDragOver" @drop="onDrop">
						<tr
							v-for="(row, rowIndex) in currentTable.rows"
							:key="rowIndex"
							class="ct-table-row"
							@click="selectRow(row)"
							:class="{ 'selected-row': row === selectedRow, 'drag-target': dragTargetRow === rowIndex }"
							:draggable="true"
							@dragstart="onDragStart(rowIndex, $event)"
							@dragenter="onDragEnter(rowIndex, $event)"
							@dragend="onDragEnd($event)"
						>
							<!-- First column for editing icons -->
							<td class="ct-row-icon">
								<p>
									<fai icon="fas fa-list" @click="moveRow(row, 'up')" />
									<fai icon="fas fa-trash" @click="confirmDeletion(deleteRow, row, 'row', $event)" />
								</p>
							</td>
							<!-- Line number as second column -->
							<td class="ct-table-cell">
								{{ row.lineNumber }}
							</td>
							<!-- File as table from the third column -->
							<td
								v-for="(cell, index) in row.cells"
								:key="index"
								class="ct-table-cell"
								:style="{ minWidth: calculateWidth(cell), maxWidth: calculateWidth(cell, true) }"
							>
								{{ cell || '-' }}
							</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>
	</div>
</template>

<script>
import { TOAST_TYPE } from '@/enums/enums';
import ConfirmationWindow from '@/components/general/ConfirmationWindow.vue';

/**
 * @vuese
 * @group Upload
 * Displays all elements of the codebook in a table format
 */
export default {
	name: 'CodebookTable',
	components: { ConfirmationWindow },
	emits: ['rowSelected', 'updateActiveTab', 'deleteTable', 'updateTables', 'updateTableRows', 'editing'],
	props: {
		tables: Array,
		selectedRow: Object,
		activeTab: Number,
	},
	data() {
		return {
			editingHeader: null,
			newHeaderValue: '',
			draggedRowIndex: null,
			dragTargetRow: null,
			confirmationDeletion: null,
		};
	},
	computed: {
		currentTable() {
			return this.tables[this.activeTab];
		},
	},
	watch: {
		activeTab(newValue, oldValue) {
			if (newValue !== oldValue) {
				this.$emit('rowSelected', null);
			}
		},
	},
	methods: {
		calculateWidth(value, isMax = false) {
			const length = value ? value.length : 0;
			if (isMax) {
				return length > 80 ? '400px' : 'auto';
			}
			if (length <= 15) return `${Math.max(length * 10, 50)}px`;
			if (length <= 25) return `${Math.max(length * 8, 100)}px`;
			return `${Math.min(length * 8, 400)}px`;
		},
		editColumn(index) {
			this.editingHeader = index;
			this.newHeaderValue = this.currentTable.columns[index];
			this.$emit('editing', true);
		},
		saveColumn(index) {
			if (!this.newHeaderValue.trim()) {
				this.$global.showToast(TOAST_TYPE.WARN, this.$t('emptyHeaderError'));
				return;
			}

			const oldHeader = this.currentTable.columns[index];
			const newHeader = this.newHeaderValue.trim();

			// Update header in columns
			this.currentTable.columns[index] = newHeader;

			// Update data in rows
			this.currentTable.rows.forEach((row) => {
				if (row.hasOwnProperty(oldHeader)) {
					row[newHeader] = row[oldHeader];
					delete row[oldHeader];
				}
			});

			this.editingHeader = null;
			this.newHeaderValue = '';
			this.$emit('updateTables', this.tables);
			this.$emit('editing', false);
		},
		deleteColumn(index) {
			const columnName = this.currentTable.columns[index];

			// Remove column
			this.currentTable.columns.splice(index, 1);

			// Remove the column from each row's cells
			this.currentTable.rows.forEach((row) => {
				row.cells.splice(index, 1);
			});

			this.$emit('updateTables', this.tables);
		},
		selectRow(row) {
			if (this.selectedRow === row) {
				this.$emit('rowSelected', null);
			} else {
				this.$emit('rowSelected', row);
			}
		},
		onDragStart(index, event) {
			this.draggedRowIndex = index;
			event.dataTransfer.effectAllowed = 'move';
		},
		onDragEnter(rowIndex, event) {
			event.preventDefault();
			this.dragTargetRow = rowIndex;
		},
		onDragEnd(event) {
			this.dragTargetRow = null;
		},
		onDrop(event) {
			event.preventDefault();
			if (this.draggedRowIndex === null || this.dragTargetRow === null) return;

			const targetRowIndex = this.dragTargetRow;
			if (this.draggedRowIndex !== targetRowIndex) {
				const draggedRow = this.currentTable.rows[this.draggedRowIndex];
				this.currentTable.rows.splice(this.draggedRowIndex, 1);
				this.currentTable.rows.splice(targetRowIndex, 0, draggedRow);
			}

			this.dragTargetRow = null;
			this.$emit('updateTables', this.tables);
		},
		moveRow(row, direction) {
			const rowIndex = this.currentTable.rows.indexOf(row);
			const newRowIndex = direction === 'up' ? rowIndex - 1 : rowIndex + 1;

			if (newRowIndex >= 0 && newRowIndex < this.currentTable.rows.length) {
				const movedRow = this.currentTable.rows.splice(rowIndex, 1)[0];
				this.currentTable.rows.splice(newRowIndex, 0, movedRow);
				this.$emit('updateTables', this.tables);
			}
		},
		deleteRow(row) {
			event.preventDefault();
			event.stopPropagation();

			const rowIndex = this.currentTable.rows.indexOf(row);
			if (rowIndex !== -1) {
				const deletedLineNumber = row.lineNumber;

				this.currentTable.rows.splice(rowIndex, 1);

				if (this.selectedRow && this.selectedRow.lineNumber === deletedLineNumber) {
					this.$emit('updateSelectedRow', null);
				}

				this.$emit('updateTableRows', {
					activeTab: this.activeTab,
					deletedLineNumber: deletedLineNumber,
				});
			}
		},
		changeTab(index) {
			this.$emit('updateActiveTab', index);
		},
		cancelEdit() {
			this.editingHeader = null;
			this.newHeaderValue = '';
			this.$emit('editing', false);
		},
		deleteTable(index) {
			this.$emit('deleteTable', index);
		},
		confirmDeletion(callback, item, type, event = null) {
			if (event) {
				event.preventDefault();
				event.stopPropagation();
			}

			this.confirmationDeletion = {
				title: this.$t('ceConfirmDeletionTitel'),
				text: this.$t('ceConfirmDeletionText'),
				cancelButton: {
					class: 'app-default-btn',
					text: this.$t('ceCancel'),
					callback: () => {
						this.isLoading = false;
						this.confirmationDeletion = null;
					},
				},
				confirmButton: {
					class: 'app-warn-btn',
					text: this.$t('ceConfirmDeletion'),
					callback: () => {
						if (type === 'row') {
							callback(item, event);
						} else if (type === 'column') {
							callback(item);
						}
						this.confirmationDeletion = null;
					},
				},
			};
		},
	},
};
</script>

<style scoped>
.ct-tab-list {
	display: flex;
	list-style: none;
}

.ct-tab-list li {
	padding: 10px 20px;
	background-color: var(--main-color-4);
	color: var(--main-color-dark);
	border: 1px solid var(--main-color-light);
}

.ct-tab-list li:hover {
	cursor: pointer;
	background-color: var(--main-color-3);
	color: var(--main-color-dark);
}

.ct-tab-list li.ct-tab-active {
	background-color: var(--main-color-5);
	color: var(--main-color-dark);
	font-weight: bold;
}

.ct-tab-content {
	margin: auto;
	overflow: auto;
	width: 100%;
	max-height: 60vh;
	border: 1px solid var(--main-color-light);
}

.ct-header-preview {
	margin: 20px 0 10px 0;
	padding: 1px;
	font-weight: normal;
}

.ct-table-content {
	width: 100%;
	border-collapse: collapse;
	table-layout: auto;
	background-color: var(--main-color-4);
}

.ct-table-header-item,
.ct-table-cell {
	text-align: left;
	word-wrap: break-word;
}

.ct-table-header-item {
	white-space: nowrap;
	height: 30px;
	padding: 10px;
	font-weight: bold;
	background-color: var(--main-color-dark);
	color: var(--main-color-light);
	border-bottom: 1px solid var(--main-color-light);
}

.ct-table-cell {
	white-space: normal;
	padding: 15px 10px;
	color: var(--main-color-dark);
	border-bottom: 1px solid var(--main-color-dark);
	border-right: 1px solid var(--main-color-dark);
}

.ct-table-row:hover .ct-table-cell,
.ct-table-row.selected-row .ct-table-cell {
	background-color: var(--main-color-5) !important;
}

.ct-table-row:hover .ct-table-cell:first-child,
.ct-table-row.selected-row .ct-table-cell:first-child {
	background: var(--main-color-dark) !important;
}

.ct-table-header-item {
	position: relative;
	text-align: left;
}

.ct-header-actions {
	margin: 0px;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.ct-header-icons {
	margin: 0 5px 0 10px;
	display: flex;
	gap: 12px;
	cursor: pointer;
	position: relative;
}

.ct-row-icon {
	min-width: 50px;
	cursor: pointer;
	background: var(--main-color-dark);
}

.ct-row-icon p {
	padding: 10px;
	display: flex;
	gap: 10px;
	justify-content: center;
}

.ct-header-input {
	font-size: 14px;
	padding: 5px;
	min-width: 150px;
	width: 100%;
}

.ct-table-row.drag-target {
	background-color: rgba(0, 0, 255, 0.1);
	border: 2px dashed rgba(0, 0, 255, 0.5);
}

.ct-table-row:hover {
	cursor: pointer;
}
</style>
