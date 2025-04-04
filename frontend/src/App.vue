<template>
	<div class="ap-wrap-content">
		<Header :userLoggedInKey="userLoggedInKey" @logoutUser="logoutUser" />
		<Breadcrumb />
		<RouterView v-slot="{ Component }" class="ap-wrap-views">
			<component :is="Component" :userLoggedInKey="userLoggedInKey" @loginUser="toggleKey" @logoutUser="logoutUser" />
		</RouterView>
		<Footer />
	</div>
</template>

<script>
import Header from '@/components/layout/Header.vue';
import Breadcrumb from '@/components/layout/Breadcrumb.vue';
import Footer from '@/components/layout/Footer.vue';
import { RouterView } from 'vue-router';
import { MSG_TYPE, ROUTE, TOAST_TYPE } from './enums/enums';

export default {
	name: 'Home',
	components: {
		RouterView,
		Header,
		Breadcrumb,
		Footer,
	},
	data() {
		return {
			userLoggedInKey: false,
			userForcedLogOut: false,
		};
	},
	created() {
		this.$store.reinitializeStore();

		if (this.$store.getToken() && !this.$store.getForceUserLogout()) this.getUser();
		else this.$store.clearStore();
	},
	methods: {
		logoutUser(forcedLogout) {
			if (!forcedLogout) {
				this.$network.postData('/api/user/logout', null, null, (err, data) => {
					try {
						if (err) this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
					} catch (error) {
						this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
					} finally {
						this.$store.clearStore();
						this.toggleKey();

						if (this.$router.currentRoute.value.name != ROUTE.HOME)
							this.$router.push({ name: ROUTE.HOME, query: { msg: MSG_TYPE.LOGOUT_SUCCESS } });
						else this.$global.showToast(TOAST_TYPE.INFO, this.$t('heUserLoggedOut'));
					}
				});
			} else {
				this.$store.clearStore();
				this.toggleKey();

				if (this.$router.currentRoute.value.name != ROUTE.HOME) this.$router.push({ name: ROUTE.HOME });
			}
		},
		// Toggle key to inform views that user data is loaded
		toggleKey() {
			this.$nextTick(() => {
				this.userLoggedInKey = !this.userLoggedInKey;
			});
		},
		getUser() {
			this.$network.getData('/api/user', null, null, (err, data) => {
				try {
					if (!err) {
						if (!this.userForcedLogOut) {
							if (Array.isArray(data.access.role)) data.access.role = data.access.role[0];
							this.$store.setToken(data.credentials.token);
							this.$store.setTokenExpiration(data.credentials.expiration);
							this.$store.setCurrentUser({ ...data });

							this.toggleKey();
						} else this.userForcedLogOut = false;
					}
					// TODO: If unauthorized logout user
					else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				}
			});
		},
	},
};
</script>

<style>
.ap-wrap-views {
	width: calc(100% - 40px);
	min-height: 78vh;
	padding: 0px 20px;
	box-sizing: border-box;
}
</style>
