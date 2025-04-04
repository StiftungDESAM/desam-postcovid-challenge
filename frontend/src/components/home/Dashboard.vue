<template>
	<div class="db-wrap-content">
		<div class="db-wrap-cards">
			<Card
				v-if="currentUser.access.permissionsGranted.includes(enumPERMISSION.ONTOLOGY_VIEW)"
				cardType="SQUARE"
				@click="navigateTo(enumROUTE.ONTOLOGY_VIEW)"
			>
				<fai icon="fas fa-hexagon-nodes" />
				<p>{{ $t('dbOntologyView') }}</p>
			</Card>
			<Card
				v-if="currentUser.access.permissionsGranted.includes(enumPERMISSION.ONTOLOGY_UPLOAD)"
				cardType="SQUARE"
				@click="navigateTo(enumROUTE.ONTOLOGY_UPLOAD)"
			>
				<fai icon="fas fa-upload" />
				<p>{{ $t('dbOntologyUpload') }}</p>
			</Card>
			<Card
				v-if="currentUser.access.permissionsGranted.includes(enumPERMISSION.ONTOLOGY_REVIEW)"
				cardType="SQUARE"
				@click="navigateTo(enumROUTE.ONTOLOGY_REVIEW)"
			>
				<fai icon="fas fa-magnifying-glass" />
				<p>{{ $t('dbOntologyReview') }}</p>
			</Card>
			<Card
				v-if="currentUser.access.permissionsGranted.includes(enumPERMISSION.DATA_UPLOAD)"
				cardType="SQUARE"
				@click="navigateTo(enumROUTE.DATA_UPLOAD)"
			>
				<fai icon="fas fa-upload" />
				<p>{{ $t('dbDataUpload') }}</p>
			</Card>
			<Card
				v-if="currentUser.access.permissionsGranted.includes(enumPERMISSION.DATA_REVIEW)"
				cardType="SQUARE"
				@click="navigateTo(enumROUTE.DATA_REVIEW)"
			>
				<fai icon="fas fa-magnifying-glass" />
				<p>{{ $t('dbDataReview') }}</p>
			</Card>
			<Card
				v-if="currentUser.access.permissionsGranted.includes(enumPERMISSION.DATA_VIEW)"
				cardType="SQUARE"
				@click="navigateTo(enumROUTE.DATA_VIEW)"
			>
				<fai icon="fas fa-database" />
				<p>{{ $t('dbDataView') }}</p>
			</Card>
			<Card
				v-if="currentUser.access.permissionsGranted.includes(enumPERMISSION.DATA_EXPORT)"
				cardType="SQUARE"
				@click="navigateTo(enumROUTE.DATA_EXPORT)"
			>
				<fai icon="fas fa-download" />
				<p>{{ $t('dbDataExport') }}</p>
			</Card>
		</div>
		<div class="db-wrap-buttons">
			<Card cardType="RECTANGLE" @click="navigateTo(enumROUTE.PROFILE)">
				<p>{{ $t('dbProfile') }}</p>
				<fai icon="fas fa-user" />
			</Card>
			<Card
				v-if="[enumROLE.SUPER_ADMIN, enumROLE.ADMIN].includes(currentUser.access.role)"
				cardType="RECTANGLE"
				@click="navigateTo(enumROUTE.ADMIN)"
			>
				<p>{{ $t('dbAdmin') }}</p>
				<fai icon="fas fa-user-tie" />
			</Card>
		</div>
	</div>
</template>

<script>
import { ROUTE, PERMISSION, ROLE } from '@/enums/enums';
import { useRouter } from 'vue-router';
import Card from '@/components/general/Card.vue';
/**
 * @vuese
 * @group Home
 * Dashboard with functionality for logged in users
 */
export default {
	name: 'Dashboard',
	components: {
		Card,
	},
	emits: [],
	props: {},
	watch: {},
	setup() {
		const router = useRouter();
		const routes = router.options.routes;
		const enumROUTE = ROUTE;
		const enumPERMISSION = PERMISSION;
		const enumROLE = ROLE;

		return { routes, enumROUTE, enumPERMISSION, enumROLE };
	},
	data() {
		return {
			currentUser: this.$store.getCurrentUser(),
		};
	},
	computed: {},
	created() {},
	mounted() {},
	beforeDestroy() {},
	methods: {
		navigateTo(dest) {
			this.$router.push({ name: dest });
		},
	},
};
</script>

<style scoped>
.db-wrap-content {
	padding: 5px 10px;
}

.db-wrap-cards {
	margin: 20px 0px;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: wrap;
}

.db-wrap-cards > * {
	margin: 10px 20px;
}

.db-wrap-buttons {
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: wrap;
}

.db-wrap-buttons div {
	width: 400px;
}
</style>
