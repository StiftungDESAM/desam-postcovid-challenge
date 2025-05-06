<template>
	<div class="aald-wrap-content">
		<div class="aald-wrap-detailed-data">
			<h2>{{ $t('duDataDetails') }}</h2>
			<!-- Careful, this next line should only be used for the prototype because of possible XSS danger through escapeParameterHtml: false setting in i18n.js -->
			<p v-if="linkedItem" v-html="$t('duDataIsLinked', { itemID: linkedItem.id, itemName: mappedItemName })"></p>
			<div class="aald-detailed-data">
				<div v-for="item in mappedItems" :key="item">
					<h3>
						{{ item.name }}
						<fai
							v-if="item.assignedMetaField"
							icon="fas fa-circle-info"
							@click="assignedMetaItem = { columnName: item.name, item: item.assignedMetaField }"
						/>
					</h3>

					<p>
						{{ (item.value !== '' ? item.value : null) ?? '-' }}
						<span v-if="item.assignedMetaField && linkedItem" class="aald-highlighted">
							({{ linkedItem[item.assignedMetaField.name] ?? '-' }})
						</span>
					</p>
				</div>
			</div>
		</div>
		<div v-if="assignedMetaItem" class="aald-wrap-assigned-meta" @click="assignedMetaItem = null">
			<div class="aald-assigned-meta" @click.stop="">
				<p v-if="assignedMetaItem.item">
					{{
						$t('duAssignedMetaData', {
							columnName: assignedMetaItem.columnName,
							metaName: assignedMetaItem.item.name,
							tag: assignedMetaItem.item.tag,
						})
					}}
				</p>
				<p v-if="assignedMetaItem.item">
					{{ $t('duIsVerified', { isVerified: assignedMetaItem.item.isVerified ? $t('duYes') : $t('duNo') }) }}
				</p>
				<p v-if="assignedMetaItem.item">
					{{ $t('duCreated', { created: $global.formatDate(assignedMetaItem.item.created, 'de') }) }}
				</p>
				<p v-if="assignedMetaItem.item">
					{{ $t('duLastUpdated', { lastUpdated: $global.formatDate(assignedMetaItem.item.lastUpdated, 'de') }) }}
				</p>
				<p v-if="!assignedMetaItem.item">{{ $t('duItemNotAssigned', { columnName: assignedMetaItem.columnName }) }}</p>
			</div>
		</div>
	</div>
</template>

<script>
/**
 * @vuese
 * @group DataUpload
 * Description
 */
export default {
	name: 'AssignedAndLinkedData',
	components: {},
	emits: [],
	props: {
		linkedItem: {
			type: Object,
			required: false,
		},
		mappedItems: {
			type: Array,
			required: true,
		},
		mappingColumn: {
			type: Object,
			required: true,
		},
	},
	watch: {},
	setup() {
		return {};
	},
	data() {
		return {
			assignedMetaItem: null,
		};
	},
	computed: {
		mappedItemName() {
			let ref = this.mappedItems.find((it) => it.tag == this.mappingColumn.tag)?.assignedMetaField?.name;
			if (ref) return this.linkedItem[ref];
			else return '-';
		},
	},
	created() {},
	mounted() {},
	beforeDestroy() {},
	methods: {},
};
</script>

<style scoped>
.aald-wrap-content {
	width: 100%;
	margin: 20px 0px;
}

.aald-wrap-detailed-data h2 {
	margin: 10px 0px 20px 0px;
	text-decoration: underline;
	font-weight: normal;
}

.aald-detailed-data {
	margin-top: 20px;
	display: flex;
	justify-content: flex-start;
	align-items: stretch;
	flex-flow: wrap;
	gap: 20px;
}

.aald-detailed-data div {
	flex: 1 1 200px;
	min-width: fit-content;
	padding-bottom: 10px;
	border-bottom: 1px solid var(--main-color-light);
	text-align: center;
}

.aald-detailed-data div h3,
.aald-detailed-data div p {
	margin: 0px;
	padding: 0px;
	text-align: start;
}

.aald-detailed-data div p span {
	margin-top: 5px;
	display: block;
}

.aald-detailed-data div h3 {
	margin-bottom: 10px;
	display: block;
	font-weight: bold;
	color: var(--main-color-light);
}

.aald-detailed-data div h3 svg:hover * {
	cursor: pointer;
	color: var(--main-color-5);
}

.aald-wrap-assigned-meta {
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
	background-color: var(--main-color-dark-80);
}

.aald-assigned-meta {
	max-width: 450px;
	padding: 10px 20px;
	border: 2px solid var(--main-color-light);
	border-radius: 10px;
	box-shadow: 0px 0px 10px 4px var(--main-color-1);
	background-color: var(--main-color-1);
}

.aald-assigned-meta p:first-child {
	text-align: start;
	margin-bottom: 10px;
}

.aald-assigned-meta p {
	text-align: end;
}
</style>

<style>
.aald-highlighted {
	font-weight: bold;
	color: var(--main-color-5);
}
</style>
