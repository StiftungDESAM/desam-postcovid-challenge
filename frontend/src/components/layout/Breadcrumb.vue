<template>
	<div class="bc-wrap-content">
		<div v-for="(crumb, index) in breadcrumbs" :key="index" class="bc-breadcrumb">
			<router-link v-if="index !== breadcrumbs.length - 1" :to="{ name: crumb.name, params: crumb.params }">
				<fai :icon="crumb.icon" /> {{ $t(crumb.label) }} <fai icon="fas fa-chevron-right" />
			</router-link>
			<span v-else> <fai :icon="crumb.icon" /> {{ $t(crumb.label) }}</span>
		</div>
	</div>
</template>

<script>
import { useRouter } from 'vue-router';
import { ROUTE } from '@/enums/enums';
/**
 * @vuese
 * @group Layout
 * Breadcrumb menu
 */
export default {
	watch: {
		$route: {
			handler(newVal) {
				this.generateBreadcrumbs();
			},
			immediate: true,
		},
	},
	setup() {
		const router = useRouter();
		const routes = router.options.routes;

		return { routes };
	},
	data() {
		return {
			matchNumberRegex: new RegExp(/\/\d+(\/|$)/g),
			matchStringRegex: new RegExp(/\/:\w+\??(\/|$)/g),
			optionalParamRegex: new RegExp(/\/:\w+\?/),
			breadcrumbs: [],
		};
	},
	mounted() {
		this.generateBreadcrumbs();
	},
	methods: {
		generateBreadcrumbs() {
			if (this.$route.name !== ROUTE.NOT_FOUND) {
				let fullPath = this.$route.fullPath.replace(this.matchNumberRegex, '/ID/');
				if (!fullPath.endsWith('/')) fullPath += '/';

				let breadcrumbs = [];
				let sortedRoutes = this.routes.sort((a, b) => a.path.split('/').length - b.path.split('/').length);

				for (let i = 0; i < sortedRoutes.length; i++) {
					let route = sortedRoutes[i];
					let hasOptionalParam = this.optionalParamRegex.test(route.path);
					let normalizedPath = route.path.replace(this.matchStringRegex, '/ID/');

					if (fullPath.includes(normalizedPath) || (hasOptionalParam && fullPath.includes(normalizedPath.replace(/\/ID\//g, '/')))) {
						breadcrumbs.push({
							label: route.meta.breadcrumb || route.name,
							name: route.name,
							params: route.params,
							icon: route.meta.icon || '',
						});
					}
				}

				this.breadcrumbs = breadcrumbs;
			} else this.breadcrumbs = [];
		},
	},
};
</script>

<style scoped>
.bc-wrap-content {
	width: 100%;
	margin: 10px 0px;
	padding: 5px;
	display: flex;
	justify-content: flex-start;
	align-items: center;
}

.bc-breadcrumb {
	display: flex;
}

.bc-breadcrumb a,
.bc-breadcrumb span {
	display: flex;
	justify-content: center;
	align-items: center;
	text-decoration: none;
}

.bc-breadcrumb a:hover {
	cursor: pointer;
	text-decoration: underline;
}

.bc-breadcrumb a svg:first-child,
.bc-breadcrumb span svg {
	height: 20px;
	margin: -2px 5px 0px 10px;
}

.bc-breadcrumb a svg:last-child {
	margin-left: 5px;
}

.bc-breadcrumb span {
	color: var(--main-color-5);
}
</style>
