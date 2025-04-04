<template>
	<div class="pa-wrap-content">
		<select class="pa-select" v-model="selectedPage" @change="$emit('selectPage', selectedPage)">
			<option v-for="page in pagination" :key="`${page.start}-${page.end}`" :value="page">
				<span v-if="page.end">{{ page.start + 1 }}-{{ page.end + 1 }}</span>
				<span v-else>{{ page.start }}</span>
			</option>
		</select>
	</div>
</template>

<script>
/**
 * @vuese
 * @group General
 * Pagination component
 */
export default {
	name: 'Pagination',
	components: {},
	emits: ['selectPage'],
	props: {
		amountElements: {
			type: Number,
			required: true,
		},
		elementsPerPage: {
			type: Number,
			required: true,
		},
	},
	watch: {
		pagination: {
			handler: function (newVal) {
				this.selectedPage = newVal[0];
				this.$emit('selectPage', this.selectedPage);
			},
		},
	},
	setup() {
		return {};
	},
	data() {
		return {
			selectedPage: null,
		};
	},
	computed: {
		pagination() {
			return this.$global.getPagination(this.amountElements, this.elementsPerPage);
		},
	},
	created() {
		this.selectedPage = this.pagination[0];
		this.$emit('selectPage', this.selectedPage);
	},
	mounted() {},
	beforeDestroy() {},
	methods: {},
};
</script>

<style scoped>
.pa-wrap-content select {
	font-size: 15px;
}
</style>
