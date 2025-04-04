<template>
	<div class="ovh-wrap-content">
		<div class="ovh-wrap-header">
			<button
				:class="exportRunning ? 'app-disabled-btn' : 'app-default-btn'"
				@click="$emit('downloadPNG')"
				:title="$t('ovDownloadGraphSelection')"
			>
				<fai class="ovh-spin-icon" icon="fas fa-download" />
			</button>
			<button class="app-default-btn" @click="$emit('fitToView')" :title="$t('ovFitToView')"><fai icon="fas fa-expand" /></button>
			<button :class="isLoading ? 'app-disabled-btn' : 'app-default-btn'" @click="$emit('reloadGraph')" :title="$t('ovReloadGraph')">
				<fai icon="fas fa-rotate-right" />
			</button>
			<button v-if="!showLegend" class="app-default-btn" @click="showLegend = true" :title="$t('ovShowLegend')">
				<fai icon="fas fa-eye" />
			</button>
			<button v-else class="app-default-btn" @click="showLegend = false" :title="$t('ovHideLegend')"><fai icon="fas fa-eye-slash" /></button>
		</div>
		<transition name="fade">
			<div v-if="showLegend" class="ovh-wrap-legend">
				<LegendElement :text="$t('ovhStakeholderColor')" :legendClass="'le-stakeholder'" />
				<LegendElement :text="$t('ovhNodeColor')" :legendClass="'le-node'" />
				<LegendElement :text="$t('ovhLeafColor')" :legendClass="'le-leaf'" />
				<LegendElement :text="$t('ovhDataColor')" :legendClass="'le-data'" />
				<LegendElement :text="$t('ovhRelationshipColor')" :legendClass="'le-relationship'" />
				<LegendElement :text="$t('ovhAddedColor')" :legendClass="'le-added'" />
				<LegendElement :text="$t('ovhDeletedColor')" :legendClass="'le-deleted'" />
				<LegendElement :text="$t('ovhModifiedColor')" :legendClass="'le-modified'" />
			</div>
		</transition>
		<div
			v-if="floatingHeader.display"
			class="ovh-floating-header"
			ref="floatingHeader"
			:style="{ top: floatingHeader.y + 'px', left: floatingHeader.x + 'px' }"
		>
			<div class="ovh-header-action">
				<p @click="!exportRunning ? $emit('downloadPNG') : null"><fai icon="fas fa-download" />{{ $t('ovDownloadGraphSelection') }}</p>
			</div>
			<div class="ovh-header-action">
				<p @click="$emit('fitToView')"><fai icon="fas fa-expand" />{{ $t('ovFitToView') }}</p>
			</div>
			<div class="ovh-header-action">
				<p @click="$emit('reloadGraph')"><fai icon="fas fa-rotate-right" />{{ $t('ovReloadGraph') }}</p>
			</div>
			<div v-if="!showLegend" class="ovh-header-action">
				<p @click="showLegend = true"><fai icon="fas fa-eye" />{{ $t('ovShowLegend') }}</p>
			</div>
			<div v-else class="ovh-header-action">
				<p @click="showLegend = false"><fai icon="fas fa-eye-slash" />{{ $t('ovHideLegend') }}</p>
			</div>
		</div>
	</div>
</template>

<script>
import LegendElement from '@/components/ontology/LegendElement.vue';

/**
 * @vuese
 * @group Ontology
 * Header of the ontology viewer
 */
export default {
	name: 'OntologyViewerHeader',
	components: { LegendElement },
	emits: ['downloadPNG', 'fitToView', 'reloadGraph', 'hideLegend'],
	props: {
		floatingHeader: {
			type: Object,
			required: true,
		},
		exportRunning: {
			type: Boolean,
			required: true,
		},
		isLoading: {
			type: Boolean,
			required: true,
		},
	},
	watch: {},
	setup() {
		return {};
	},
	data() {
		return {
			showLegend: false,
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
.ovh-wrap-content {
	width: 100%;
}

.ovh-wrap-header {
	width: 100%;
	box-sizing: border-box;
	text-align: end;
}

.ovh-wrap-header button {
	margin: 5px 5px 5px 0px;
	font-size: 15px;
}

.ovh-floating-header {
	padding: 10px;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: column;
	position: absolute;
	box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
	border: 1px solid var(--main-color-light);
	border-radius: 5px;
	background-color: var(--main-color-dark-bb);
	z-index: 1000;
}

.ovh-header-action {
	width: 100%;
	text-align: start;
}

.ovh-header-action p {
	width: 100%;
	margin: 5px;
	display: flex;
	justify-content: flex-start;
	align-items: center;
	text-align: start;
}

.ovh-header-action p:hover {
	cursor: pointer;
	text-decoration: underline;
}

.ovh-header-action p svg {
	margin-right: 10px;
}

.ovh-wrap-legend {
	width: fit-content;
	position: absolute;
	top: 5px;
	left: 5px;
	border: 1px solid var(--main-color-light);
	border-radius: 5px;
	background-color: var(--main-color-dark-bb);
}

.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.25s ease-in-out;
}

.fade-enter-from,
.fade-leave-to {
	opacity: 0;
}
</style>
