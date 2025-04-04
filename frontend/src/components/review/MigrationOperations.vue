<template>
	<div class="mo-wrap-content">
		<Table :config="migrationOperationsTableConfig" @selectItem="$emit('highlightMigration', $event)" />
	</div>
</template>

<script>
import Table from '@/components/general/Table.vue';
import { tableConfig } from '@/components/review/migrationOperationsTableConfig.js';
/**
 * @vuese
 * @group Review
 * Displays migration operations of the ontology
 */
export default {
	name: 'MigrationOperations',
	components: { Table },
	emits: ['highlightMigration'],
	props: {
		migrations: {
			type: Array,
			required: true,
		},
	},
	watch: {},
	setup() {
		return {};
	},
	data() {
		return {
			migrationOperationsTableConfig: tableConfig,
		};
	},
	computed: {},
	created() {
		this.migrationOperationsTableConfig.data.values = this.migrations;
	},
	mounted() {},
	beforeDestroy() {},
	methods: {},
};
</script>

<style scoped>
.mo-wrap-content {
	margin: 10px 0px;
	padding: 2px;
	position: relative;
	overflow: hidden;
}
</style>
