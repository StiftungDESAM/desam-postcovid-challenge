<template>
	<div class="he-wrap-content">
		<div class="he-wrap-logo">
			<router-link :to="{ name: 'Home' }">
				<img :src="logo" :alt="$t('heLogo')" />
			</router-link>
		</div>
		<div class="he-wrap-title">
			<p>Modell für die evolutionäre Integration heterogener Daten-Quellen</p>
		</div>
		<div class="he-wrap-navigation">
			<router-link :to="{ name: 'Home' }">
				<p>{{ $t('heHome') }}</p>
			</router-link>
			<router-link v-if="currentUser" :to="{ name: 'Profile' }">
				<p>{{ $t('heProfile') }}</p>
			</router-link>
			<router-link :to="{ name: 'LegalNotice' }">
				<p>{{ $t('heLegalNotice') }}</p>
			</router-link>
			<a v-if="currentUser" @click="logoutUser">
				<p>{{ $t('heLogout') }}</p>
			</a>
		</div>
	</div>
</template>

<script>
import logo from '@/assets/img/Logo.png';
import logoMEVODAT from '@/assets/img/Logo_MEVODAT.png';
import { TOAST_TYPE } from '@/enums/enums';

/**
 * @vuese
 * @group Layout
 * Header of the website
 */
export default {
	name: 'Header',
	emits: ['logoutUser'],
	props: {
		// Toggle key that is used to requery the user from the store
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
	data() {
		return {
			logo: logoMEVODAT,
			currentUser: this.$store.getCurrentUser(),
		};
	},
	methods: {
		// @vuese
		// Logs a user out of the system
		logoutUser() {
			// Fires once a user has clicked on the logout button
			// @arg Is false because the logout wasn't forced by the system
			this.$emit('logoutUser', false);
		},
	},
};
</script>

<style scoped>
.he-wrap-content {
	width: 100%;
	height: 50px;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: row;
	padding: 5px;
	border-bottom: 1px solid var(--main-color-light);
}

.he-wrap-logo {
	width: 50px;
	height: 50px;
	margin-right: 10px;
}

.he-wrap-logo img {
	width: 46px;
	height: 46px;
	margin: 2px;
}

.he-wrap-title {
	flex: 1 1 400px;
	font-size: 17px;
}

.he-wrap-navigation {
	flex: 1 1 calc(100% - 460px);
	height: 50px;
	padding-right: 10px;
	display: flex;
	justify-content: flex-end;
	align-items: center;
}

.he-wrap-navigation a {
	margin: 0px 5px;
	padding: 10px;
	border-radius: 5px;
	background-color: none;
	color: var(--main-color-light);
	text-decoration: underline;
	transition: background-color 0.2s ease-in-out;
}

.he-wrap-navigation a:hover {
	cursor: pointer;
	background-color: var(--main-color-2);
}
</style>
