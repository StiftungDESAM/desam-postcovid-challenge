<template>
	<div class="lo-wrap-content">
		<LoadingSpinner v-if="isLoading" :wrapperClass="'lo-wrap-content'" />
		<div v-show="!showForgotPassword" class="lo-wrap-login">
			<h2 class="lo-header">{{ $t('loLogin') }}</h2>
			<div class="lo-wrap-inputs" @keyup.enter="credentialsEntered ? loginUser() : null">
				<InputField
					v-model="login.email"
					:placeholder="$t('loEmail')"
					:labelText="$t('loEmail')"
					:inputType="'email'"
					:autocompleteType="'email'"
				/>
				<InputField
					v-model="login.password"
					:placeholder="$t('loPassword')"
					:labelText="$t('loPassword')"
					:inputType="'password'"
					:autocompleteType="'current-password'"
				/>
				<InputField v-model="stayLoggedIn" :labelText="$t('loStayLoggedIn')" :inputType="'checkbox'" />
			</div>
			<div class="lo-wrap-btn">
				<button :class="credentialsEntered ? 'app-success-btn' : 'app-disabled-btn'" @click="loginUser">{{ $t('loLoginUser') }}</button>
			</div>
			<div class="lo-wrap-links">
				<p class="lo-underline-text" @click="showForgotPassword = true">{{ $t('loForgotPassword') }}?</p>
				<em>
					<span>{{ $t('loNoAccount') }}?</span>
					<span>{{ $t('loGoTo') }}</span>
					<span class="lo-underline-text" @click="$emit('openRegistration')">{{ $t('loRegistration') }}</span>
				</em>
			</div>
		</div>
		<div v-show="showForgotPassword" class="lo-wrap-forgot-password">
			<h2 class="lo-header">{{ $t('loRequestResetLink') }}</h2>
			<div class="lo-wrap-inputs" @keyup.enter="resetEmail ? requestResetLink() : null">
				<InputField
					v-model="resetEmail"
					:placeholder="$t('loEmail')"
					:labelText="$t('loEmail')"
					:inputType="'email'"
					@newValue="checkEmail"
				/>
			</div>
			<div class="lo-wrap-btn">
				<button class="app-default-btn" @click="showForgotPassword = false">{{ $t('loBack') }}</button>
				<button :class="resetEmailIsValid ? 'app-warn-btn' : 'app-disabled-btn'" :disabled="!resetEmail" @click="requestResetLink">
					{{ $t('loRequestResetPassword') }}
				</button>
			</div>
		</div>
	</div>
</template>

<script>
import { REQUEST_STATUS, TOAST_TYPE } from '@/enums/enums';
import InputField from '@/components/general/InputField.vue';
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
/**
 * @vuese
 * @group Home
 * Provides Login functionality
 */
export default {
	name: 'Login',
	components: { InputField, LoadingSpinner },
	emits: ['openRegistration', 'closeLogin', 'loginUser'],
	props: {},
	watch: {},
	setup() {
		return {};
	},
	data() {
		return {
			login: {
				email: null,
				password: null,
			},
			stayLoggedIn: false,
			resetEmail: null,
			isLoading: false,
			showForgotPassword: false,
			test: null,
		};
	},
	computed: {
		credentialsEntered() {
			let credentialsEntered = true;

			if (!this.login.email || this.login.email.trim() == '') credentialsEntered = false;
			else if (!this.login.password || this.login.password.trim() == '') credentialsEntered = false;

			return credentialsEntered;
		},
		resetEmailIsValid() {
			return this.resetEmail ? this.$global.emailIsValid(this.resetEmail) : false;
		},
	},
	created() {},
	mounted() {},
	beforeDestroy() {},
	methods: {
		checkEmail(email) {
			if (email && !this.resetEmailIsValid) this.$global.showToast(TOAST_TYPE.WARN, this.$t('loInvalidMail'));
		},
		loginUser() {
			this.isLoading = true;

			this.$network.postData('/api/user/login', { email: this.login.email, password: this.login.password }, null, (err, data) => {
				try {
					if (!err) {
						this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('loLoginSuccessfull'));

						if (this.stayLoggedIn) this.$store.setStayLoggedIn(true);

						if (Array.isArray(data.access.role)) data.access.role = data.access.role[0];
						this.$store.setToken(data.credentials.token);
						this.$store.setTokenExpiration(data.credentials.expiration);
						this.$store.setCurrentUser(data);

						this.login = {
							email: null,
							password: null,
						};
						this.stayLoggedIn = false;

						this.$emit('loginUser');
					} else if (err.status == REQUEST_STATUS.FORBIDDEN) this.$global.showToast(TOAST_TYPE.WARN, this.$t('loAccountNotVerified'));
					else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.isLoading = false;
				}
			});
		},
		requestResetLink() {
			this.isLoading = true;

			this.$network.postData('/api/user/request-password-reset', { email: this.resetEmail }, null, (err, data) => {
				try {
					this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('loResetEmailSent'));
					this.$emit('closeLogin', true);
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.showForgotPassword = false;
					this.isLoading = false;
					this.resetEmail = null;
				}
			});
		},
	},
};
</script>

<style scoped>
.lo-wrap-content {
	max-width: 80vw;
	max-height: 90vh;
	padding: 20px;
	border: 1px solid var(--main-color-light);
	border-radius: 5px;
	overflow: auto;
	position: relative;
	background-color: var(--main-color-1);
}

.lo-wrap-forgot-password,
.lo-wrap-login {
	width: 100%;
}

.lo-header {
	margin-bottom: 20px;
	text-align: center;
	font-weight: normal;
}

.lo-wrap-inputs {
	width: 100%;
	margin: 10px 0px;
}

.lo-wrap-inputs > div {
	margin-bottom: 10px;
}

.lo-wrap-btn {
	width: 100%;
	text-align: center;
}

.lo-wrap-btn button {
	min-width: 200px;
	margin: 0px 5px 10px 5px;
	padding: 10px 20px;
	font-size: 18px;
}

.lo-wrap-links {
	width: 100%;
	text-align: center;
}

.lo-wrap-links p {
	margin: 10px 0px;
}

.lo-wrap-links em span {
	padding-right: 5px;
}

.lo-underline-text {
	text-decoration: underline;
	cursor: pointer;
}
</style>
