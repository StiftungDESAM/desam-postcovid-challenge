<template>
	<div class="ta-wrap-content" :id="`wrapper-${tableID}`">
		<div v-if="config.header" class="ta-wrap-functions-header" ref="functionsHeader" :id="`functionsHeader-${tableID}`">
			<div v-if="config.header.searchbar" class="ta-wrap-search">
				<label for="search">{{ config.header.searchbar.label }}</label>
				<input id="search" type="text" :placeholder="config.header.searchbar.placeholder" v-model="searchInput" @input="recomputeCells" />
			</div>
			<div v-if="config.header.sort" class="ta-wrap-sort">
				<label>{{ config.header.sort.label }}</label>
				<select class="ta-select" v-model="sortBy" @change="recomputeCells">
					<option v-for="opt in config.header.sort.options" :key="opt.value" :value="opt.value">{{ opt.text }}</option>
				</select>
			</div>
			<div v-if="config.header.pagination" class="ta-wrap-pagination">
				<Pagination
					:amountElements="config.data.values.length"
					:elementsPerPage="config.header.pagination.itemsPerPage"
					@selectPage="selectPage"
				/>
			</div>
		</div>
		<div class="ta-wrap-table" ref="table" :id="`table-${tableID}`">
			<div class="ta-wrap-header" :id="`header-${tableID}`">
				<div v-if="config.functions?.rows?.delete" class="ta-header-spacer"></div>
				<div data-cords="spacer" :class="[...getClassesForSpacer()]" ref="spacer"></div>
				<div
					v-for="col in config.data.columns"
					:key="col.ref.join('')"
					:ref="col.ref.join('')"
					:data-cords="col.ref.join('')"
					:class="['ta-header-element']"
					:id="`headerElement-${tableID}`"
				>
					<div class="ta-cell-icon-wrapper">
						<fai icon="fas fa-circle-xmark" class="ta-error-icon" @click.stop="clickIcon('ERROR', col, null)" />
						<fai icon="fas fa-triangle-exclamation" class="ta-warning-icon" @click.stop="clickIcon('WARNING', col, null)" />
					</div>
					<div
						v-if="(config.functions?.columns?.delete || config.functions?.columns?.edit) && !col.ignoreFunctions"
						class="ta-wrap-header-icons"
					>
						<fai
							v-if="config.functions?.columns?.delete && currentHeader?.ref.join('') != col.ref.join('')"
							icon="fas fa-trash"
							class="ta-delete-icon"
							@click.stop="$emit('deleteColumn', col.ref)"
						/>
						<fai
							v-if="config.functions?.columns?.edit && currentHeader?.ref.join('') != col.ref.join('')"
							icon="fas fa-pen"
							class="ta-edit-icon"
							@click.stop="setupEditHeader(col)"
						/>
						<fai
							v-if="currentHeader?.ref.join('') == col.ref.join('')"
							icon="fas fa-floppy-disk"
							class="ta-save-icon"
							@click.stop="editHeader"
						/>
					</div>
					<p v-if="currentHeader?.ref.join('') != col.ref.join('')">{{ col.text }}</p>
					<input v-else-if="currentHeader?.ref.join('') == col.ref.join('')" v-model="newHeaderName" @keyup.enter="editHeader" />
				</div>
			</div>
			<div class="ta-wrap-body" :id="`body-${tableID}`">
				<div
					v-for="item in paginatedItems"
					:key="item"
					:data-cords="getValue(item, { ref: [config.data.key] })"
					:class="[...getClassesForRow(item)]"
					:id="`${tableID}-${getValue(item, { ref: [config.data.key] })}`"
				>
					<div class="ta-cell-icon-wrapper">
						<fai icon="fas fa-circle-xmark" class="ta-error-icon" @click.stop="clickIcon('ERROR', null, item)" />
						<fai icon="fas fa-triangle-exclamation" class="ta-warning-icon" @click.stop="clickIcon('WARNING', null, item)" />
					</div>
					<div v-if="config.functions?.rows?.delete" class="ta-wrap-row-icons">
						<fai icon="fas fa-trash" class="ta-delete-icon" @click.stop="$emit('deleteRow', item)" />
					</div>
					<div
						v-for="col in config.data.columns"
						:key="col.ref.join('')"
						:ref="col.ref.join('')"
						:data-cords="`${col.ref.join('')}-${getValue(item, { ref: [config.data.key] })}`"
						:class="[...getClassesForCell(col.ref, item)]"
						:id="`bodyElement-${tableID}`"
						@click="selectItem(col.ref, item)"
						@mouseenter="setColor(col.ref, item, false)"
						@mouseleave="setColor(col.ref, item, true)"
					>
						{{ getValue(item, col) }}
						<div class="ta-cell-icon-wrapper">
							<fai icon="fas fa-circle-xmark" class="ta-error-icon" @click.stop="clickIcon('ERROR', col, item)" />
							<fai icon="fas fa-triangle-exclamation" class="ta-warning-icon" @click.stop="clickIcon('WARNING', col, item)" />
						</div>
					</div>
				</div>
				<div v-if="paginatedItems.length === 0" class="ta-no-data">
					{{ $t('taNoElementsFound') }}
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import Pagination from '@/components/general/Pagination.vue';
import { SORT_ORDER, TABLE_SELECTION, TABLE_SELECTION_AMOUNT } from '@/enums/enums';
import { faChevronRight } from '@fortawesome/free-solid-svg-icons';
import * as uuid from 'uuid';
/**
 * @vuese
 * @group General
 * Generic table component
 *
 * Config structure:
 *
 * {
 *      layout: {
 * 			table: {
 * 				minWidth: String // The min width of the table. The unit (px,%,...) will be defined in the string itself
 * 				maxWidth: String // The max width of the table. The unit (px,%,...) will be defined in the string itself
 * 				minHeight: String // The min height of the table. The unit (px,%,...) will be defined in the string itself
 * 				maxHeight: String // The max height of the table. The unit (px,%,...) will be defined in the string itself
 * 			},
 * 			columns:{
 *         		minWidth: Number // The min width of the table column in px. Default is 100
 *          	maxWidth: Number // The max width of the table column in px. Default is 750
 * 				padding: { // The padding values for the columns. Will be 15px for all by default
 * 					top: Number, // The top padding of the column
 * 					right: Number, // The right padding of the column
 * 					bottom: Number, // The bottom padding of the column
 * 					left: Number, // The left padding of the column
 * 				}
 * 			}
 *      },
 *      header: {
 *          searchbar: { // If false or undefined the searchbar wont be rendered
 *              label: String, // Text label for the search input field
 *              placeholder: String, // Placeholder text displayed inside the search input
 *          },
 *          sort: { // If false or undefined the sort by wont be rendered
 *              label: String, // Label for the sorting dropdown
 *              options: [
 *                  {
 *                      value: String, // Value of the sort option. Must follow this pattern: <key>-<sortDirection> e.g name-desc
 *                      text: String  // Displayed text for the sort option
 *                  },
 *              ],
 *              sortMapping: [ // Maps certain properties of the data to the sort option
 *                  {
 *                      key: [String] // Replace key with the name of the key from the sort options. Holds at least one String that is the key to a data property. e.g name: ['user.firstName', 'user.lastName']
 *                  }
 *              ]
 *          },
 *          pagination: { // If false or undefined the pagination wont be rendered
 *              itemsPerPage: Number, // Specifies how many items to display per page
 *          },
 *      },
 * 		functions:{
 * 			selection:{
 * 				mode: String, // Defines how the user click selection works. Can be ROW_SELECT for rows, COLUMN_SELECT for columns or DISABLED it no selection should be allowed. Default is ROW_SELECT
 * 				amount: String // Defines how many rows of columns can be selected. Can be SINGLE or MULTIPLE. Default is SINGLE
 * 			}
 * 			columns:{
 * 				delete: Boolean // If true displays a delete icon for a certain column
 * 				edit: Boolean // If true displays a edit icon for a certain column header tha can be used to change the header text
 * 			},
 * 			rows:{
 * 				delete: Boolean // If true displays a delete icon for a certain row
 * 			},
 * 			cells:{
 *
 * 			},
 * 		},
 * 		styling: { // Styling options for the table
 * 			customClasses: [ // Array of custom classes that can be passed. Need to be in a style tag without scope
 * 				{ // If both colRef and rowRef are set then the cell will be targeted
 * 					className: "String", // Name of the class
 * 					colRef: "String", // Ref of the column. If set alone will target the whole column
 * 					rowRef: "String" // Ref of the row. If set alone will target the whole row
 * 				}
 * 			]
 * 		},
 *      data: {
 *          key: String // Identifier for the item in the passed data array. Needs to be unique
 *          columns: [
 *              {
 *                  ref: ['String'], // Property that contains an array of values (e.g. ['dateStart', 'dateEnd'])
 *                  text: String, // Column name
 *                  formatter: Function?, // Optional converter that parses the data a certain way
 *              },
 *          ],
 *          values: [
 *              Object // The data for the table rows. Must match the provided columns and ref structure
 *          ]
 *       },
 *   }
 */
export default {
	name: 'Table',
	components: { Pagination },
	emits: ['selectItem', 'deleteColumn', 'deleteRow', 'clickedErrorIcon', 'clickedWarningIcon'],
	props: {
		config: {
			type: Object,
			required: true,
		},
		resetSelected: {
			type: Boolean,
			required: false,
		},
		startValue: {
			type: [String, Number],
			required: false,
		},
	},
	watch: {
		'config.data.values': {
			handler: function (newValue) {
				if (newValue.length > 0) {
					this.$nextTick(() => {
						if (this.startValue != null && this.startValue != undefined && this.selectedItems.length == 0) this.setStartValue();
						if (this.config?.functions?.selection?.mode == TABLE_SELECTION.DISABLED) this.disableHover();
						// if (this.config?.styling?.customClasses) this.setupCustomClasses();
						this.setupMinWidths();
					});
				}
			},
			deep: true,
		},
		// 'config.styling': {
		// 	handler: function (newValue) {
		// 		this.setupCustomClasses();
		// 	},
		// 	deep: true,
		// },
		resetSelected: {
			handler: function () {
				this.selectedItems = [];
			},
		},
	},
	setup() {
		return {};
	},
	data() {
		return {
			tableID: uuid.v4().substring(0, 8),
			minWidths: {},
			searchInput: null,
			debounceTimeout: null,
			sortBy: this.config?.header?.sort?.options[0]?.value,
			selectedPage: null,
			selectedItems: [],
			standardValues: {
				columnMinWidth: 100,
				columnMaxWidth: 750,
				columnPadding: 15,
				tableWidth: '100%',
				tableHeight: '100%',
			},
			currentHeader: null,
			newHeaderName: null,
		};
	},
	computed: {
		searchedItems() {
			if (!this.config.header?.searchbar) return this.config.data.values;
			if (!this.searchInput) return this.config.data.values;

			const searchInputUpper = this.searchInput.toUpperCase();

			return this.config.data.values.filter((item) => {
				const searchStr = this.config.data.columns
					.map((col) => {
						let value = this.getValue(item, col);

						return value ? value.toString() : '';
					})
					.join(' ')
					.toUpperCase();

				return searchStr.includes(searchInputUpper);
			});
		},
		sortedItems() {
			if (!this.config.header?.sort) return this.searchedItems;

			const [key, direction] = this.sortBy.split('-');
			const sortBy = this.config.header.sort.sortMapping[key];
			const order = direction == 'desc' ? SORT_ORDER.DESC : SORT_ORDER.ASC;

			return this.$global.sortArray(this.searchedItems, sortBy, order);
		},
		paginatedItems() {
			if (!this.config.header?.pagination) return this.sortedItems;

			if (this.selectedPage && this.selectedPage.end) return this.sortedItems.slice(this.selectedPage.start, this.selectedPage.end + 1);
			else return this.sortedItems;
		},
		highlightedCells() {
			const selectMode = this.config.functions?.selection?.mode || TABLE_SELECTION.ROW_SELECT;
			const ref = { ref: [this.config.data.key] };

			let highlightedCells = {};

			this.config.data.columns.forEach((col) => {
				const colRef = col.ref.join('');
				this.config.data.values.forEach((row) => {
					const rowRef = this.getValue(row, ref);
					let highlighted = false;

					if (selectMode == TABLE_SELECTION.ROW_SELECT) highlighted = this.selectedItems.some((it) => this.getValue(it, ref) == rowRef);
					else if (selectMode == TABLE_SELECTION.COLUMN_SELECT) highlighted = this.selectedItems.some((it) => it.ref.join('') == colRef);

					highlightedCells[`${colRef}_${rowRef}`] = highlighted;
				});
			});

			return highlightedCells;
		},
		customClasses() {
			let customClasses = {};

			this.config.styling?.customClasses?.forEach((customClass) => {
				let identifier =
					customClass.colRef == null
						? customClass.rowRef
						: customClass.rowRef == null
							? customClass.colRef
							: `${customClass.colRef}_${customClass.rowRef}`;

				if (customClasses[identifier]) customClasses[identifier].push(customClass.className);
				else customClasses[identifier] = [customClass.className];
			});

			return customClasses;
		},
	},
	created() {},
	mounted() {
		if (this.config?.data?.values?.length > 0) {
			if (this.startValue != null && this.startValue != undefined) this.setStartValue();
			this.setupMinWidths();
		}
		if (this.config?.functions?.selection?.mode == TABLE_SELECTION.DISABLED) this.disableHover();
		// if (this.config?.styling?.customClasses) this.setupCustomClasses();
		window.addEventListener('resize', this.resizeListener);
	},
	beforeUnmount() {
		window.removeEventListener('resize', this.resizeListener);
	},
	methods: {
		resizeListener() {
			this.setHeaderWidth();
			this.debouncedRecomputeCells();
		},
		disableHover() {
			document.querySelectorAll(`#bodyElement-${this.tableID}`).forEach((el) => {
				el.style.cursor = 'default';
			});
		},
		setTableLayout() {
			let wrapper = document.querySelector(`#wrapper-${this.tableID}`);
			let functionsHeader = document.querySelector(`#functionsHeader-${this.tableID}`);
			let table = document.querySelector(`#table-${this.tableID}`);

			const tableHeightOffset = functionsHeader ? `${functionsHeader.offsetHeight}px` : '0px';
			const minWidth = this.config.layout?.table?.minWidth || this.standardValues.tableWidth;
			const maxWidth = this.config.layout?.table?.maxWidth || this.standardValues.tableWidth;
			const minHeight = this.config.layout?.table?.minHeight || this.standardValues.tableHeight;
			const maxHeight = this.config.layout?.table?.maxHeight || this.standardValues.tableHeight;

			if (wrapper) wrapper.style.cssText = `min-width: ${minWidth}; max-width: ${maxWidth}; min-height: ${minHeight}; max-height: ${maxHeight}`;
			if (table)
				table.style.cssText = `min-width: ${minWidth}; max-width: ${maxWidth}; min-height: calc(${minHeight} - ${tableHeightOffset}); max-height: calc(${maxHeight} - ${tableHeightOffset})`;
		},
		setupCustomClasses() {
			// TODO: Remove previous custom classes again if new data is rendered
			// if (this.config.styling?.customClasses?.length > 0) {
			// 	this.$nextTick(() => {
			// 		let customClassesForCols = [];
			// 		let customClassesForRows = [];
			// 		let customClassesForCells = [];
			// 		this.config.styling.customClasses.forEach((it) => {
			// 			if (it.colRef && !it.rowRef) customClassesForCols.push(it);
			// 			else if (!it.colRef && it.rowRef) customClassesForRows.push(it);
			// 			else if (it.colRef && it.rowRef) customClassesForCells.push(it);
			// 		});
			// 		customClassesForCols.forEach((colClass) => {
			// 			this.$refs[colClass.colRef]?.forEach((ref) => {
			// 				ref.classList.add(colClass.className);
			// 			});
			// 		});
			// 		customClassesForRows.forEach((rowClass) => {
			// 			if (rowClass.rowRef == 'spacer') this.$refs.spacer?.classList.add(rowClass.className);
			// 			else {
			// 				const row = document.getElementById(`${this.tableID}-${rowClass.rowRef}`);
			// 				row?.classList.add(rowClass.className);
			// 			}
			// 		});
			// 		if (customClassesForCells.length > 0) {
			// 			let minRowRef = null;
			// 			let maxRowRef = null;
			// 			this.paginatedItems.forEach((item) => {
			// 				const value = this.getValue(item, { ref: [this.config.data.key] });
			// 				if (!minRowRef) minRowRef = value;
			// 				else if (minRowRef != null && value < minRowRef) minRowRef = value;
			// 				if (!maxRowRef) maxRowRef = value;
			// 				else if (maxRowRef != null && value > maxRowRef) maxRowRef = value;
			// 			});
			// 			const filteredCustomClassesForCells = customClassesForCells.filter((it) => it.rowRef >= minRowRef && it.rowRef <= maxRowRef);
			// 			const cells = Array.from(document.querySelectorAll(`#bodyElement-${this.tableID}`));
			// 			cells.forEach((cell, idx) => {
			// 				setTimeout(() => {
			// 					cell.classList.add(
			// 						filteredCustomClassesForCells.find((it) => cell.dataset?.cords == `${it.colRef}-${it.rowRef}`)?.className
			// 					);
			// 				}, 1);
			// 			});
			// 		}
			// 	});
			// }
		},
		setStartValue() {
			const selectMode = this.config.functions?.selection?.mode || TABLE_SELECTION.ROW_SELECT;
			if (selectMode != TABLE_SELECTION.DISABLED) {
				if (selectMode == TABLE_SELECTION.ROW_SELECT) {
					let ref = { ref: [this.config.data.key] };
					this.selectedItems = [this.paginatedItems.find((it) => this.getValue(it, ref) == this.startValue)];
				} else {
					this.selectedItems = [
						{
							ref: [this.startValue],
							data: this.paginatedItems.map((it) => it[this.startValue]),
						},
					];
				}
			}
		},
		debouncedRecomputeCells() {
			clearTimeout(this.debounceTimeout);
			document.querySelector(`#table-${this.tableID}`).style.overflow = 'hidden';

			this.debounceTimeout = setTimeout(() => {
				document.querySelector(`#table-${this.tableID}`).style.overflow = 'auto';
				this.recomputeCells();
			}, 200);
		},
		recomputeCells() {
			this.$nextTick(() => {
				this.setupMinWidths();
			});
		},
		setupMinWidths() {
			const refs = this.config.data.columns.map((it) => it.ref.join(''));
			this.setPadding();
			this.setTableLayout();
			this.resetMinWidths(refs);
			this.getMinWidths(refs);
			this.correctMinWidths(refs);
			this.setMinWidths(refs);
			this.setHeaderWidth();
		},
		setPadding() {
			const top = this.config.layout?.columns?.padding?.top || this.standardValues.columnPadding;
			const right = this.config.layout?.columns?.padding?.right || this.standardValues.columnPadding;
			const bottom = this.config.layout?.columns?.padding?.bottom || this.standardValues.columnPadding;
			const left = this.config.layout?.columns?.padding?.left || this.standardValues.columnPadding;
			const padding = `${top}px ${right}px ${bottom}px ${left}px`;

			document.querySelectorAll(`#headerElement-${this.tableID}`).forEach((el) => {
				el.style.padding = padding;
			});

			document.querySelectorAll(`#bodyElement-${this.tableID}`).forEach((el) => {
				el.style.padding = padding;
			});
		},
		resetMinWidths(refs) {
			this.minWidths = {};
			refs.forEach((col) => {
				this.$refs[col]?.forEach((ref) => {
					ref.style.width = '';
					ref.style.minWidth = '';
				});
			});
		},
		getContentWidth(el) {
			if (!el) return 0;
			const width = getComputedStyle(el).width;

			// Ensure width is a valid number
			const parsedWidth = parseFloat(width);
			return isNaN(parsedWidth) ? 0 : parsedWidth;
		},
		getMinWidths(refs) {
			refs.forEach((col) => {
				this.$refs[col]?.forEach((ref) => {
					const colWidth = this.getContentWidth(ref);

					if (colWidth > 0) {
						this.minWidths = {
							...this.minWidths,
							[col]: Math.max(this.minWidths[col] || 0, colWidth),
						};
					}
				});
			});
		},
		correctMinWidths(refs) {
			refs.forEach((col) => {
				let maxWidth = this.config?.layout?.columns?.maxWidth ? this.config?.layout?.columns?.maxWidth : this.standardValues.columnMaxWidth;
				let minWidth = this.config?.layout?.columns?.minWidth ? this.config?.layout?.columns?.minWidth : this.standardValues.columnMinWidth;

				if (this.minWidths[col] > maxWidth) this.minWidths[col] = maxWidth;
				else if (this.minWidths[col] < minWidth) this.minWidths[col] = minWidth;
			});

			const table = document.querySelector(`#table-${this.tableID}`);
			const sum = Object.values(this.minWidths).reduce((acc, val) => acc + val, 0);
			const width = table.offsetWidth;
			const scrollbarWidth = table.scrollHeight > table.clientHeight ? 17 : 0;

			if (sum < width) {
				const amountCols = Object.keys(this.minWidths).length;
				const paddingWidth =
					amountCols *
					((this.config.layout?.columns?.padding?.left || this.standardValues.columnPadding) +
						(this.config.layout?.columns?.padding?.right || this.standardValues.columnPadding));

				// -2px because of the border width
				let widthPerCol = (width - paddingWidth - sum - scrollbarWidth - 2) / amountCols;
				refs.forEach((col) => (this.minWidths[col] = this.minWidths[col] + widthPerCol));
			}
		},
		setMinWidths(refs) {
			refs.forEach((col) => {
				this.$refs[col]?.forEach((ref) => {
					const width = `${this.minWidths[col]}px`;
					ref.style.width = width;
					ref.style.minWidth = width;
				});
			});
		},
		setHeaderWidth() {
			if (this.$refs.functionsHeader) this.$refs.functionsHeader.style.width = `${this.$refs.table.offsetWidth}px`;
		},
		selectPage(page) {
			this.selectedPage = page;
			this.recomputeCells();
			// this.setupCustomClasses();
		},
		getClassesForSpacer() {
			let classes = ['ta-icon-header-spacer'];

			if (this.customClasses['spacer']) classes = [...classes, ...this.customClasses['spacer']];

			return classes;
		},
		getClassesForRow(item) {
			let classes = ['ta-body-row'];
			const rowRef = this.getValue(item, { ref: [this.config.data.key] });

			if (this.customClasses[rowRef]) classes = [...classes, ...this.customClasses[rowRef]];

			return classes;
		},
		getClassesForCell(col, item) {
			let classes = ['ta-body-element'];
			const colRef = col.join('');
			const rowRef = this.getValue(item, { ref: [this.config.data.key] });

			if (this.highlightedCells[`${colRef}_${rowRef}`]) classes.push('ta-highlight-cell');
			if (this.customClasses[`${colRef}_${rowRef}`]) classes = [...classes, ...this.customClasses[`${colRef}_${rowRef}`]];
			if (this.customClasses[colRef]) classes = [...classes, ...this.customClasses[colRef]];

			return classes;
		},
		setColor(colIdentifier, item, reset) {
			const selectMode = this.config.functions?.selection?.mode || TABLE_SELECTION.ROW_SELECT;

			if (selectMode == TABLE_SELECTION.ROW_SELECT) {
				const row = document.getElementById(`${this.tableID}-${this.getValue(item, { ref: [this.config.data.key] })}`);

				row.querySelectorAll('.ta-body-element').forEach((it) => {
					if (!reset) it.style.backgroundColor = 'var(--main-color-5)';
					else it.style.backgroundColor = '';
				});
			} else if (selectMode == TABLE_SELECTION.COLUMN_SELECT) {
				const refs = this.$refs[colIdentifier.join('')];

				refs.forEach((ref) => {
					if (!reset) ref.style.backgroundColor = 'var(--main-color-5)';
					else ref.style.backgroundColor = '';
				});
			}
		},
		selectItem(colIdentifier, item) {
			const selectMode = this.config.functions?.selection?.mode || TABLE_SELECTION.ROW_SELECT;
			if (selectMode == TABLE_SELECTION.ROW_SELECT) {
				const selectedItem = item;
				const ref = { ref: [this.config.data.key] };
				const itemValue = this.getValue(selectedItem, ref);

				let itemAlreadySelected = this.selectedItems.some((item) => this.getValue(item, ref) == itemValue);
				if (itemAlreadySelected) this.selectedItems = this.selectedItems.filter((item) => this.getValue(item, ref) != itemValue);
				else {
					if (this.config.functions?.selection?.amount == TABLE_SELECTION_AMOUNT.MULTIPLE) this.selectedItems.push(selectedItem);
					else this.selectedItems = [selectedItem];
				}

				this.$emit('selectItem', selectedItem);
			} else if (selectMode == TABLE_SELECTION.COLUMN_SELECT) {
				let selectedItem = {
					ref: colIdentifier,
					data: this.paginatedItems.map((it) => {
						if (colIdentifier.length > 1) {
							let data = {};

							colIdentifier.forEach((id) => {
								data[id] = it[id];
							});
							return data;
						} else return it[colIdentifier.join('')];
					}),
				};

				let itemAlreadySelected = this.selectedItems.some((item) => item?.ref?.join('') == selectedItem.ref.join(''));
				if (itemAlreadySelected) this.selectedItem = this.selectedItems.filter((item) => item?.ref?.join('') != selectedItem.ref.join(''));
				else {
					if (this.config.functions?.selection?.amount == TABLE_SELECTION_AMOUNT.MULTIPLE) this.selectedItems.push(selectedItem);
					else this.selectedItems = [selectedItem];
				}

				this.$emit('selectItem', selectedItem);
			}
		},
		clickIcon(type, col, row) {
			let colRef = null;
			let rowRef = null;

			if (col) colRef = col.ref.join('');
			if (row) rowRef = this.getValue(row, { ref: [this.config.data.key] });

			this.$emit(type == 'ERROR' ? 'clickedErrorIcon' : 'clickedWarningIcon', { colRef: colRef, rowRef: rowRef });
		},
		// highlightCell(colIdentifier, item) {
		// 	const selectMode = this.config.functions?.selection?.mode || TABLE_SELECTION.ROW_SELECT;
		// 	if (selectMode == TABLE_SELECTION.ROW_SELECT) {
		// 		const ref = { ref: [this.config.data.key] };
		// 		const itemValue = this.getValue(item, ref);

		// 		return this.selectedItems.some((it) => this.getValue(it, ref) == itemValue);
		// 	} else if (selectMode == TABLE_SELECTION.COLUMN_SELECT) {
		// 		const itemValue = colIdentifier.join('');

		// 		return this.selectedItems.some((it) => it.ref.join('') == itemValue);
		// 	}
		// },
		getValue(item, col) {
			let values = [];
			col.ref.forEach((ref) => {
				values.push(ref.split('.').reduce((obj, key) => obj?.[key], item));
			});

			return col.formatter && typeof col.formatter == 'function' ? col.formatter(...values) : values.join(' ');
		},
		setupEditHeader(col) {
			this.currentHeader = col;
			this.newHeaderName = col.text;
		},
		editHeader() {
			this.$emit('editHeader', { ref: this.currentHeader.ref.join(''), text: this.newHeaderName });
			this.currentHeader = null;
			this.newHeaderName = null;
		},
	},
};
</script>

<style scoped>
.ta-wrap-content {
	width: 100%;
}

.ta-wrap-functions-header {
	margin: auto;
	display: flex;
	justify-content: flex-start;
	align-items: flex-end;
	flex-flow: wrap;
	border: 1px solid var(--main-color-light);
	border-bottom: 0px;
	box-sizing: border-box;
	text-align: center;
	background-color: var(--main-color-dark);
}

.ta-wrap-search,
.ta-wrap-sort {
	padding: 5px;
}

.ta-wrap-search label,
.ta-wrap-sort label {
	padding: 0px 0px 5px 2px;
	display: block;
	font-size: 15px;
	text-align: start;
}

.ta-wrap-search input,
.ta-wrap-sort select {
	width: 100%;
	font-size: 15px;
}

.ta-wrap-pagination {
	flex: 1 1 50px;
	height: 100%;
	padding: 5px;
	display: flex;
	justify-content: flex-end;
}

.ta-wrap-table {
	width: 100%;
	max-width: fit-content;
	max-height: 60vh;
	margin: auto;
	overflow: auto;
	position: relative;
	border: 1px solid var(--main-color-light);
}

.ta-wrap-header {
	width: 100%;
	min-height: 40px;
	max-height: 95px;
	display: flex;
}

.ta-header-element {
	/* min-width: fit-content; */
	border-bottom: 1px solid var(--main-color-light);
	font-weight: bold;
	background-color: var(--main-color-dark) !important;
	overflow-y: auto;
	overflow-x: hidden;
}

.ta-header-spacer {
	min-width: 30px;
	border-bottom: 1px solid var(--main-color-light);
	background-color: var(--main-color-dark) !important;
}

.ta-icon-header-spacer {
	width: 0px;
	border-bottom: 1px solid var(--main-color-light);
	background-color: var(--main-color-dark) !important;
}

.ta-wrap-header-icons {
	width: 100%;
	margin-bottom: 10px;
	display: flex;
	justify-content: center;
	align-items: center;
	gap: 5px;
}

.ta-wrap-row-icons {
	min-width: 30px;
	display: flex;
	justify-content: center;
	align-items: center;
	border-bottom: 1px solid var(--main-color-dark);
	border-right: 1px solid var(--main-color-dark);
}

.ta-wrap-row-icons svg * {
	color: var(--main-color-dark);
}

.ta-wrap-row-icons svg *,
.ta-wrap-header-icons svg * {
	cursor: pointer;
}

.ta-delete-icon:hover * {
	color: var(--main-color-error);
}

.ta-header-element p {
	margin: 0px;
	padding: 0px;
	color: var(--main-color-light) !important;
}

.ta-wrap-body {
	width: fit-content;
	min-height: 100px;
	overflow: hidden;
}

.ta-wrap-body div {
	background-color: var(--main-color-4);
}

.ta-highlight-user {
	background-color: var(--main-color-5) !important;
}

.ta-no-data {
	width: 100%;
	height: calc(100% - 40px);
	min-height: 100px;
	display: flex;
	justify-content: center;
	align-items: center;
	position: absolute;
	top: 40px;
	left: 0px;
	font-size: 20px;
	background-color: var(--main-color-1) !important;
	color: var(--main-color-5);
}

.ta-no-data p {
	margin: 0px;
}

.ta-body-row {
	width: 100%;
	display: flex;
}

.ta-body-element {
	border-bottom: 1px solid var(--main-color-dark);
	color: var(--main-color-dark);
	cursor: pointer;
}

.ta-highlight-cell {
	background-color: var(--main-color-5) !important;
	cursor: pointer;
	color: var(--main-color-dark) !important;
}

.ta-cell-icon-wrapper {
	/* flex: 1 1 100%; */
	margin-top: 5px;
	text-align: end;
	background-color: transparent !important;
}

.ta-header-element .ta-cell-icon-wrapper {
	margin-top: 0px;
	margin-bottom: 5px;
	text-align: center;
}

.ta-body-row > .ta-cell-icon-wrapper {
	margin-top: 0px;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: column;
	border-bottom: 1px solid var(--main-color-dark);
}

.ta-cell-icon-wrapper > svg {
	/* width: 25px; */
	font-size: 20px;
	margin-left: 5px;
	display: none;
	cursor: pointer;
}

.ta-warning-icon *,
.ta-error-icon * {
	filter: drop-shadow(14px 14px 1px var(--main-color-dark));
}

.ta-error-icon * {
	color: var(--main-color-error) !important;
}

.ta-warning-icon * {
	color: var(--main-color-warn) !important;
}

.ta-error-icon:hover * {
	color: var(--main-color-error-80) !important;
}

.ta-warning-icon:hover * {
	color: var(--main-color-warn-80) !important;
}
</style>
