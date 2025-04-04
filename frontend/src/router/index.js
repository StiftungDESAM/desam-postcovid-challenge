import Admin from '@/views/Admin.vue';
import Profile from '@/views/Profile.vue';
import DataExport from '@/views/DataExport.vue';
import DataReview from '@/views/DataReview.vue';
import DataUpload from '@/views/DataUpload.vue';
import DataView from '@/views/DataView.vue';
import FeedbackView from '@/views/FeedbackView.vue';
import Home from '@/views/Home.vue';
import NotFound from '@/views/NotFound.vue';
import OntologyView from '@/views/OntologyView.vue';
import OntologyReview from '@/views/OntologyReview.vue';
import OntologyUpload from '@/views/OntologyUpload.vue';
import LegalNotice from '@/views/LegalNotice.vue';
import PasswordReset from '@/views/PasswordReset.vue';
import { createRouter, createWebHistory } from 'vue-router';
import { reactive } from 'vue';
import { checkAccess } from '@/router/auth';
import { ROUTE, PERMISSION } from '@/enums/enums';

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: '/',
			name: ROUTE.HOME,
			component: Home,
			meta: { permissions: [], breadcrumb: 'bcHome', icon: 'fas fa-home' },
		},
		{
			path: '/admin',
			name: ROUTE.ADMIN,
			component: Admin,
			meta: { permissions: [PERMISSION.ADMIN], breadcrumb: 'bcAdmin', icon: 'fas fa-user-tie' },
			beforeEnter: checkAccess,
		},
		{
			path: '/profile',
			name: ROUTE.PROFILE,
			component: Profile,
			meta: { permissions: [], breadcrumb: 'bcProfile', icon: 'fas fa-user' },
			beforeEnter: checkAccess,
		},
		{
			path: '/data',
			name: ROUTE.DATA_VIEW,
			component: DataView,
			meta: { permissions: [PERMISSION.DATA_VIEW], breadcrumb: 'bcDataView', icon: 'fas fa-database' },
			beforeEnter: checkAccess,
		},
		{
			path: '/data/export',
			name: ROUTE.DATA_EXPORT,
			meta: { permissions: [PERMISSION.DATA_EXPORT], breadcrumb: 'bcDataExport', icon: 'fas fa-download' },
			component: DataExport,
			beforeEnter: checkAccess,
		},
		{
			path: '/data/review/:reviewID?',
			name: ROUTE.DATA_REVIEW,
			meta: { permissions: [PERMISSION.DATA_REVIEW], breadcrumb: 'bcDataReview', icon: 'fas fa-magnifying-glass' },
			component: DataReview,
			beforeEnter: checkAccess,
		},
		{
			path: '/data/upload',
			name: ROUTE.DATA_UPLOAD,
			component: DataUpload,
			meta: { permissions: [PERMISSION.DATA_UPLOAD], breadcrumb: 'bcDataUpload', icon: 'fas fa-upload' },
			beforeEnter: checkAccess,
		},
		{
			path: '/feedback/:feedbackID',
			name: ROUTE.FEEDBACK_VIEW,
			component: FeedbackView,
			meta: { permissions: [], breadcrumb: 'bcFeedbackView', icon: 'fas fa-comment-dots' },
			beforeEnter: checkAccess,
		},
		{
			path: '/ontology',
			name: ROUTE.ONTOLOGY_VIEW,
			component: OntologyView,
			meta: { permissions: [PERMISSION.ONTOLOGY_VIEW], breadcrumb: 'bcOntologyView', icon: 'fas fa-hexagon-nodes' },
			beforeEnter: checkAccess,
		},
		{
			path: '/ontology/review/:reviewID?',
			name: ROUTE.ONTOLOGY_REVIEW,
			component: OntologyReview,
			meta: { permissions: [PERMISSION.ONTOLOGY_REVIEW], breadcrumb: 'bcOntologyReview', icon: 'fas fa-magnifying-glass' },
			beforeEnter: checkAccess,
		},
		{
			path: '/ontology/upload',
			name: ROUTE.ONTOLOGY_UPLOAD,
			component: OntologyUpload,
			meta: { permissions: [PERMISSION.ONTOLOGY_UPLOAD], breadcrumb: 'bcOntologyUpload', icon: 'fas fa-upload' },
			beforeEnter: checkAccess,
		},
		{
			path: '/password-reset',
			name: ROUTE.PASSWORD_RESET,
			component: PasswordReset,
			meta: { permissions: [], breadcrumb: 'bcPasswordReset', icon: 'fas fa-key' },
		},
		{
			path: '/legal-notice',
			name: ROUTE.LEGAL_NOTICE,
			component: LegalNotice,
			meta: { permissions: [], breadcrumb: 'bcLegalNotice', icon: 'fas fa-scale-balanced' },
		},
		{
			path: '/:pathMatch(.*)*',
			name: ROUTE.NOT_FOUND,
			component: NotFound,
			meta: { permissions: [], breadcrumb: 'bcNotFound', icon: 'fas fa-circle-question' },
		},
	],
	scrollBehavior(to) {
		if (to.hash) {
			return {
				el: to.hash,
				behavior: 'smooth',
			};
		}
	},
});

export const routeHistory = reactive({
	lastRoute: null,
	referrer: document.referrer,
});

// Track previous route before each navigation
router.beforeEach((to, from, next) => {
	if (from.name) routeHistory.lastRoute = from;

	routeHistory.referrer = document.referrer;

	next();
});

export default router;
