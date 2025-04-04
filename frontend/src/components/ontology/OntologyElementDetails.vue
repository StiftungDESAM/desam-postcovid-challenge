<template>
	<transition name="slide">
		<div v-if="details" class="oed-wrap-content">
			<fai icon="fas fa-circle-xmark" @click="$emit('resetDetails')" />
			<h2>{{ $t(details.from) }}</h2>
			<div v-if="details.data.id" :class="['oed-wrap-input', getOwnModificationClass('id')]">
				<label>{{ $t('oedID') }}</label>
				<input type="text" :value="details.data.id" disabled />
			</div>
			<div v-if="details.data.stakeholder_id" :class="['oed-wrap-input', getOwnModificationClass('stakeholder_id')]">
				<label>{{ $t('oedStakeholderID') }}</label>
				<input type="text" :value="details.data.stakeholder_id" disabled />
			</div>
			<div v-if="details.data.name" :class="['oed-wrap-input', getOwnModificationClass('name')]">
				<label>{{ $t('oedName') }}</label>
				<input type="text" :value="details.data.name" disabled />
			</div>
			<div v-if="details.data.value" :class="['oed-wrap-input', getOwnModificationClass('value')]">
				<label>{{ $t('oedValue') }}</label>
				<textarea :value="details.data.value" disabled />
			</div>
			<div v-if="details.data.tag" :class="['oed-wrap-input', getOwnModificationClass('tag')]">
				<label>{{ $t('oedTag') }}</label>
				<input type="text" :value="details.data.tag" disabled />
			</div>
			<div v-if="details.data.cardinality" :class="['oed-wrap-input', getOwnModificationClass('cardinality')]">
				<label>{{ $t('oedCardinality') }}</label>
				<input type="text" :value="details.data.cardinality" disabled />
			</div>
			<div v-if="details.data.is_stakeholder != undefined" :class="['oed-wrap-input', getOwnModificationClass('is_stakeholder')]">
				<label>{{ $t('oedIsStakeholder') }}</label>
				<input type="text" :value="details.data.is_stakeholder ? $t('oedYes') : $t('oedNo')" disabled />
			</div>
			<div v-if="details.data.is_leaf != undefined" :class="['oed-wrap-input', getOwnModificationClass('is_leaf')]">
				<label>{{ $t('oedIsLeaf') }}</label>
				<input type="text" :value="details.data.is_leaf ? $t('oedYes') : $t('oedNo')" disabled />
			</div>
			<div v-if="details.data.is_verified != undefined" :class="['oed-wrap-input', getOwnModificationClass('is_verified')]">
				<label>{{ $t('oedIsVerified') }}</label>
				<input type="text" :value="details.data.is_verified ? $t('oedYes') : $t('oedNo')" disabled />
			</div>
			<div v-if="details.data.created" :class="['oed-wrap-input', getOwnModificationClass('created')]">
				<label>{{ $t('oedCreated') }}</label>
				<input type="text" :value="$global.formatDate(new Date(details.data.created), 'de')" disabled />
			</div>
			<div v-if="details.data.last_updated" :class="['oed-wrap-input', getOwnModificationClass('last_updated')]">
				<label>{{ $t('oedLastUpdated') }}</label>
				<input type="text" :value="$global.formatDate(new Date(details.data.last_updated), 'de')" disabled />
			</div>
			<div class="oed-divider"></div>
			<div
				v-if="details.from != oeEnum.DATA && details.data.source && details.data.target?.ONTOLOGY_ELEMENT != oeEnum.DATA"
				class="oed-wrap-relationship"
			>
				<p>
					<span :class="getNeighborModificationClass(details.data.source)">{{ details.data.source.name }}</span>
					<span>
						<strong :class="getOwnModificationClass()">{{ details.data.name }}[{{ details.data.cardinality }}]</strong>
					</span>
					<span :class="getNeighborModificationClass(details.data.target)">{{ details.data.target.name }}</span>
				</p>
			</div>
			<div v-if="details.from != oeEnum.DATA && details.data.neighbors" class="oed-wrap-neighbors">
				<label>{{ $t('oedNeighbors') }}</label>
				<div v-for="neighbor in filteredNeighbors" :key="neighbor.target ? neighbor.target.id : neighbor.source.id" class="oed-neighbor">
					<p v-if="neighbor.target">
						<span>-</span>
						<span>
							<strong :class="getOwnModificationClass()">{{ details.data.name }}</strong>
						</span>
						<span :class="getNeighborModificationClass(neighbor)"> {{ neighbor.name }}[{{ neighbor.cardinality }}]</span>
						<span :class="getNeighborModificationClass(neighbor.target)">{{ neighbor.target.name }}</span>
					</p>
					<p v-else>
						<span>-</span>
						<span :class="getNeighborModificationClass(neighbor.source)">{{ neighbor.source.name }}</span>
						<span :class="getNeighborModificationClass(neighbor)"> {{ neighbor.name }}[{{ neighbor.cardinality }}]</span>
						<span>
							<strong :class="getOwnModificationClass()">{{ details.data.name }}</strong>
						</span>
					</p>
				</div>
				<div v-if="details.data.neighbors.length == 0" class="oed-no-neighbors">
					<em>{{ $t('oedNoNeighbors') }}</em>
				</div>
			</div>
		</div>
	</transition>
</template>

<script>
import { ONTOLOGY_ELEMENT } from '@/enums/enums';

/**
 * @vuese
 * @group Ontology
 * Details of a ontology element (node or relationship)
 */
export default {
	name: 'OntologyElementDetails',
	components: {},
	emits: ['resetDetails'],
	props: {
		details: {
			type: Object,
			required: false,
		},
	},
	watch: {},
	setup() {
		const oeEnum = ONTOLOGY_ELEMENT;
		return { oeEnum };
	},
	data() {
		return {};
	},
	computed: {
		filteredNeighbors() {
			return this.details.data.neighbors.filter((it) => it.target?.name || it.source);
		},
	},
	created() {},
	mounted() {},
	beforeDestroy() {},
	methods: {
		getOwnModificationClass(key) {
			if (this.details.data.modified?.includes(key)) return 'oed-modified';
			else if (this.details.data.added) return 'oed-added';
			else if (this.details.data.deleted) return 'oed-deleted';
			else return null;
		},
		getNeighborModificationClass(neighbor) {
			if (Object.keys(neighbor).some((key) => neighbor.modified?.includes(key))) return 'oed-modified';
			else if (neighbor.added) return 'oed-added';
			else if (neighbor.deleted) return 'oed-deleted';
			else return null;
		},
	},
};
</script>

<style scoped>
.oed-wrap-content {
	width: 300px;
	height: calc(100% - 40px);
	margin: 20px;
	padding: 20px;
	position: absolute;
	right: 0;
	top: 1px;
	box-sizing: border-box;
	border: 1px solid var(--main-color-light);
	border-radius: 10px;
	overflow: auto;
	background-color: var(--main-color-dark-bb);
}

.oed-wrap-content::-webkit-scrollbar-track,
.oed-wrap-content::-webkit-scrollbar-thumb {
	border-radius: 10px !important;
}

.oed-wrap-content svg {
	position: absolute;
	top: 5px;
	right: 5px;
	font-size: 25px;
	cursor: pointer;
}

.oed-wrap-content svg:hover * {
	color: var(--main-color-5);
}

.oed-wrap-content h2 {
	font-weight: normal;
	text-decoration: underline;
}

.oed-wrap-input {
	width: 100%;
	padding-top: 10px;
}

.oed-wrap-input label,
.oed-wrap-neighbors label {
	display: block;
	margin: 0px 0px 5px 2px;
	font-weight: normal;
}

.oed-modified input {
	background-color: var(--main-color-warn) !important;
	color: var(--main-color-dark) !important;
}

.oed-added input {
	background-color: var(--main-color-success) !important;
	color: var(--main-color-dark) !important;
}

.oed-deleted input {
	background-color: var(--main-color-error) !important;
}

.oed-modified {
	color: var(--main-color-warn) !important;
	font-weight: bold;
}

.oed-added {
	color: var(--main-color-success) !important;
	font-weight: bold;
}

.oed-deleted {
	color: var(--main-color-error) !important;
	font-weight: bold;
}

.oed-wrap-input input,
.oed-wrap-input textarea {
	width: 100%;
	margin: 0px;
	padding: 5px 10px;
	font-size: 13px;
	background-color: var(--main-color-2);
	color: var(--main-color-light);
}

.oed-wrap-input textarea {
	field-sizing: content;
	max-height: 200px;
}

.oed-divider {
	width: 100%;
	margin: 20px auto 5px auto;
	border-top: 1px solid var(--main-color-light);
}

.oed-wrap-neighbors {
	width: 100%;
	display: flex;
	justify-content: flex-start;
	align-items: flex-start;
	flex-flow: column;
}

.oed-neighbor {
	margin: 5px 0px;
	display: flex;
	justify-content: flex-start;
	align-items: center;
}

.oed-neighbor p,
.oed-wrap-relationship p {
	font-size: 14px;
	word-wrap: break-word;
	white-space: normal;
	display: flex;
	flex-wrap: wrap;
	gap: 10px;
}

.oed-neighbor span,
.oed-wrap-relationship span {
	white-space: nowrap;
}

.oed-neighbor span strong,
.oed-wrap-relationship span strong {
	color: var(--main-color-5);
}

.oed-neighbor svg {
	font-size: 15px;
	position: static;
}

.oed-no-neighbors em {
	font-size: 13px;
	color: var(--main-color-5);
}

.slide-enter-active,
.slide-leave-active {
	transition: transform 0.3s ease-in-out;
}

.slide-enter-from,
.slide-leave-to {
	transform: translateX(100%);
}
</style>
