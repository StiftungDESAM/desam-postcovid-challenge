<template>
	<div class="ho-wrap-content">
		<div class="ho-wrap-heading">
			<h1>{{ $t('hoPostCovidChallenge') }}</h1>
		</div>
		<div class="ho-wrap-counters">
			<Counter v-for="stat in stats" :key="stat.translation" :stat="stat" />
		</div>
		<div v-if="currentUser" class="ho-wrap-dashboard">
			<Dashboard />
		</div>
		<div class="ho-wrap-highlights">
			<StudyHighlights />
		</div>
		<div v-if="!currentUser" class="ho-wrap-registration-login">
			<em class="ho-motivation-text">
				<span>{{ $t('hoContributeData') }}</span>
				<span>{{ $t('hoCreateAccount') }}</span>
			</em>
			<button class="app-default-btn" @click="openRegistration">{{ $t('hoOpenRegistration') }}</button>
			<em class="ho-login-text">
				<span>{{ $t('hoAccountAvailable') }}</span>
				<span>{{ $t('hoGoTo') }}</span>
				<span @click="openLogin">{{ $t('hoLogin') }}</span
				>.
			</em>
		</div>
		<div v-show="showLogin || showRegistration" class="ho-center-content" @click="closeWindow(false)" @mousedown="clickDownRegistered = true">
			<Login
				v-show="showLogin"
				@click.stop
				@mousedown.stop
				@openRegistration="openRegistration"
				@closeLogin="closeWindow($event)"
				@loginUser="loginUser"
			/>
			<Registration v-show="showRegistration" @click.stop @mousedown.stop @openLogin="openLogin" @closeRegistration="closeWindow($event)" />
		</div>
	</div>
</template>

<script>
import { TOAST_TYPE, MSG_TYPE, ROUTE } from '@/enums/enums';
import { useRouter } from 'vue-router';
import { useRoute } from 'vue-router';
import stats from '@/assets/dummy/stats';
import Counter from '@/components/home/Counter.vue';
import Dashboard from '@/components/home/Dashboard.vue';
import StudyHighlights from '@/components/home/StudyHighlights.vue';
import Login from '@/components/home/Login.vue';
import Registration from '@/components/home/Registration.vue';

/**
 * @vuese
 * @group Home
 * Home of the website
 */
export default {
	name: 'Home',
	components: {
		Counter,
		Dashboard,
		StudyHighlights,
		Login,
		Registration,
	},
	emits: ['loginUser', 'logoutUser'],
	props: {
		userLoggedInKey: {
			type: Boolean,
			required: true,
		},
	},
	watch: {
		userLoggedInKey: {
			handler: function () {
				this.currentUser = this.$store.getCurrentUser();
			},
		},
	},
	setup() {
		const router = useRouter();
		const route = useRoute();
		const routes = router.options.routes;
		const enumROUTE = ROUTE;

		return { routes, route, enumROUTE };
	},
	data() {
		return {
			currentUser: this.$store.getCurrentUser(),
			showLogin: false,
			showRegistration: false,
			clickDownRegistered: false,
			// TODO: Replace mocked stats
			stats: stats,
		};
	},
	computed: {},
	mounted() {
		this.checkForQueryMsg();
		window.addEventListener('resize', this.resizeListener);
	},
	beforeUnmount() {
		window.removeEventListener('resize', this.resizeListener);
	},
	methods: {
		resizeListener() {
			if (document.querySelector('.ho-center-content') && (this.showLogin || this.showRegistration)) this.adjustLoadingPosition();
		},
		checkForQueryMsg() {
			let msg = this.route.query.msg;
			if (msg != null) {
				if (msg == MSG_TYPE.UNAUTHORIZED) {
					this.$emit('logoutUser', true);
					this.$global.showToast(TOAST_TYPE.WARN, this.$t('warnUnauthorizedAccess'));
				} else if (msg == MSG_TYPE.FORBIDDEN) this.$global.showToast(TOAST_TYPE.WARN, this.$t('warnForbiddenAccess'));
				else if (msg == MSG_TYPE.REGISTRATION_SUCCESS) this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('successRegistrationSuccessful'));
				else if (msg == MSG_TYPE.LOGOUT_SUCCESS) this.$global.showToast(TOAST_TYPE.INFO, this.$t('infoLogoutSuccessful'));
			}
			this.$router.push({ query: {} });
		},
		openRegistration() {
			this.showRegistration = true;
			this.showLogin = false;
			this.adjustLoadingPosition();
		},
		openLogin() {
			this.showLogin = true;
			this.showRegistration = false;
			this.adjustLoadingPosition();
		},
		adjustLoadingPosition() {
			let wrapper = document.documentElement;
			wrapper.style.overflowY = 'hidden';
			this.$nextTick(() => {
				document.querySelector('.ho-center-content').style.top = `${window.scrollY}px`;
			});
		},
		loginUser() {
			this.$emit('loginUser');
			this.closeWindow(true);
		},
		closeWindow(force) {
			if (force || this.clickDownRegistered) {
				this.showLogin = false;
				this.showRegistration = false;
				document.documentElement.style.overflowY = 'auto';
				this.clickDownRegistered = false;
			}
		},
	},
};
</script>

<style scoped>
.ho-wrap-heading h1 {
	width: 100%;
	margin-bottom: 20px;
	font-size: 80px;
	font-weight: normal;
	text-align: center;
}

.ho-wrap-counters {
	width: 100%;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: wrap;
}

.ho-wrap-counters div {
	margin: auto;
}

.ho-wrap-highlights {
	width: 100%;
	margin: 10px 0px;
}

.ho-wrap-registration-login {
	width: 100%;
	margin: 25px 20px;
	text-align: center;
}

.ho-wrap-registration-login button {
	margin: 15px 0px;
	padding: 10px 20px;
	font-size: 20px;
}

.ho-motivation-text span {
	padding: 2px 0px;
	display: block;
}

.ho-login-text {
	display: block;
}

.ho-login-text span {
	padding-right: 5px;
}

.ho-login-text span:last-child {
	padding-right: 0px;
	text-decoration: underline;
	cursor: pointer;
}

.ho-center-content {
	width: 100vw;
	height: 100vh;
	position: absolute;
	left: 0px;
	display: flex;
	justify-content: center;
	align-items: center;
	background-color: var(--main-color-dark-80);
}
</style>
