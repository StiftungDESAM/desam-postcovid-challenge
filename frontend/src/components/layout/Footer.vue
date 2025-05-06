<template>
	<div class="fo-wrap-content">
		<h2>MEVODAT - Post-Covid Datenplattform</h2>
		<div class="fo-wrap-links">
			<a href="https://desam.de/ueber-uns" target="_blank">DESAM Stiftung</a>
			<span>|</span>
			<a href="https://www.medizin.uni-tuebingen.de/de/das-klinikum/einrichtungen/institute/allgemeinmedizin" target="_blank"
				>Universität Tübingen</a
			>
			<span>|</span>
			<a href="https://www.ukw.de/startseite/" target="_blank">Universität Würzburg</a>
			<span>|</span>
			<a href="https://www.uni-kiel.de/de/" target="_blank">Universität Kiel</a>
			<span>|</span>
			<a href="https://artemis.reutlingen-university.de" target="_blank">Hochschule Reutlingen (Artemis)</a>
			<span>|</span>
			<a
				href="https://www.medizin.uni-tuebingen.de/de/das-klinikum/einrichtungen/institute/informationstechnologie-und-medizininformatik/medic"
				target="_blank"
				>Universitätsklinikum Tübingen (DIZ/meDIC)</a
			>
			<span>|</span>
			<a
				href=" https://uni-tuebingen.de/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/lehrstuehle/methods-in-medical-informatics/research-and-publications/research-projects/#c2238606"
				target="_blank"
				>Universität Tübingen (ZIV)</a
			>

			<!--<router-link :to="{ name: enumROUTE.HOME }">/</router-link>
			<router-link :to="{ name: enumROUTE.ADMIN }">/admin</router-link>
			<router-link :to="{ name: enumROUTE.PROFILE }">/profile</router-link>
			<router-link :to="{ name: enumROUTE.ONTOLOGY_VIEW }">/ontology</router-link>
			<router-link :to="{ name: enumROUTE.ONTOLOGY_UPLOAD }">/ontology/upload</router-link>
			<router-link :to="{ name: enumROUTE.ONTOLOGY_REVIEW, params: { reviewID: 1 } }">/ontology/review/:reviewID</router-link>
			<router-link :to="{ name: enumROUTE.DATA_VIEW }">/data</router-link>
			<router-link :to="{ name: enumROUTE.DATA_UPLOAD }">/data/upload</router-link>
			<router-link :to="{ name: enumROUTE.DATA_REVIEW, params: { reviewID: 1 } }">/data/review/:reviewID</router-link>
			<router-link :to="{ name: enumROUTE.DATA_EXPORT }">/data/export</router-link>
			<router-link :to="{ name: enumROUTE.FEEDBACK_VIEW, params: { feedbackID: 1 } }">/feedback/:feedbackID</router-link>
			<router-link :to="{ name: enumROUTE.LEGAL_NOTICE }">/legal-notice</router-link>
			<router-link :to="{ name: enumROUTE.PASSWORD_RESET, query: { resetCode: 123 } }">/password-reset</router-link>

			<router-link :to="{ path: '/notfound' }">/not-found</router-link> -->
		</div>
		<div class="fo-wrap-links">
			<router-link :to="{ name: enumROUTE.LEGAL_NOTICE, hash: '#impressum' }">Impressum</router-link>
			<span>|</span>
			<router-link :to="{ name: enumROUTE.LEGAL_NOTICE, hash: '#data-privacy' }">Datenschutz</router-link>
		</div>
	</div>
</template>

<script>
import { ROUTE } from '@/enums/enums';
/**
 * @vuese
 * @group Layout
 * Footer of the website
 */
export default {
	name: 'Footer',
	components: {},
	emits: [],
	props: {},
	watch: {},
	setup() {
		const enumROUTE = ROUTE;

		return { enumROUTE };
	},
	data() {
		return {};
	},
	computed: {},
	created() {},
	mounted() {},
	beforeDestroy() {},
	methods: {},
};
</script>

<style scoped>
.fo-wrap-content {
	width: 100%;
	padding: 15px 5px 0px 5px;
	border-top: 1px solid var(--main-color-light);
	text-align: center;
}

.fo-wrap-content div a {
	display: block;
	max-width: fit-content;
	text-decoration: none;
}

.fo-wrap-content div a:hover {
	cursor: pointer;
	text-decoration: underline;
}

.fo-wrap-links {
	margin: 10px;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: wrap;
	gap: 10px;
}

.fo-wrap-links a,
.fo-wrap-links router-link {
	text-decoration: underline;
}
</style>
