<template>
	<div class="pr-wrap-content">
		<LoadingSpinner v-if="isLoading" :wrapperClass="'pr-wrap-content'" />
		<h2 class="pr-header">{{ $t('prHeader') }}</h2>
		<div class="pr-wrap-inputs" @keyup.enter="resetPassword">
			<div class="pr-wrap-password">
				<transition name="fade">
					<div v-if="showPasswordHint" class="pr-wrap-password-hint">
						<p>
							<fai v-if="!$global.checkPasswordLength(passwordReset)" icon="fas fa-circle-xmark" class="pr-invalid" />
							<fai v-else icon="fas fa-circle-check" class="pr-valid" />
							<span>{{ $t('rePasswordLength') }}</span>
						</p>
						<p>
							<fai v-if="!$global.checkPasswordUpperCase(passwordReset)" icon="fas fa-circle-xmark" class="pr-invalid" />
							<fai v-else icon="fas fa-circle-check" class="pr-valid" />
							<span>{{ $t('reUpperCaseLetter') }}</span>
						</p>
						<p>
							<fai v-if="!$global.checkPasswordLowerCase(passwordReset)" icon="fas fa-circle-xmark" class="pr-invalid" />
							<fai v-else icon="fas fa-circle-check" class="pr-valid" />
							<span>{{ $t('reLowerCaseLetter') }}</span>
						</p>
						<p>
							<fai v-if="!$global.checkPasswordSpecialLetter(passwordReset)" icon="fas fa-circle-xmark" class="pr-invalid" />
							<fai v-else icon="fas fa-circle-check" class="pr-valid" />
							<span>{{ $t('reSpecialLetter') }}</span>
						</p>
					</div>
				</transition>
				<InputField
					v-model="passwordReset"
					:placeholder="$t('prReset')"
					:labelText="$t('prReset')"
					:inputType="'password'"
					@newValue="checkPassword"
					@focus="showPasswordHint = true"
					@blur="showPasswordHint = false"
				/>
			</div>
			<InputField
				v-model="passwordResetRepeat"
				:placeholder="$t('prResetRepeat')"
				:labelText="$t('prResetRepeat')"
				:inputType="'password'"
				@newValue="checkPasswordRepeat"
			/>
		</div>
		<div class="pr-wrap-btn">
			<button :class="passwordsEntered ? 'app-default-btn' : 'app-disabled-btn'" @click="resetPassword">
				{{ $t('prConfirmPasswordReset') }}
			</button>
		</div>
	</div>
</template>

<script>
import { MSG_TYPE, TOAST_TYPE } from '@/enums/enums';
import { ROUTE } from '@/enums/enums.js';
import { useRoute } from 'vue-router';
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
import InputField from '@/components/general/InputField.vue';
/**
 * @vuese
 * @group Password Reset
 * Provides password reset functionalitys
 */
export default {
	name: 'PasswordReset',
	components: { InputField, LoadingSpinner },
	emits: [],
	props: {},
	watch: {},
	setup() {
		const route = useRoute();

		return { route };
	},
	data() {
		return {
			isLoading: false,
			passwordReset: null,
			passwordResetRepeat: null,
			code: null,
			showPasswordHint: false,
		};
	},
	computed: {
		passwordsEntered() {
			let passwordsEntered = true;

			if (!this.$global.passwordIsValid(this.passwordReset, false)) passwordsEntered = false;
			else if (!this.passwordReset || this.passwordReset.trim() == '') passwordsEntered = false;
			else if (!this.passwordResetRepeat || this.passwordResetRepeat.trim() == '') passwordsEntered = false;
			else if (this.passwordReset !== this.passwordResetRepeat) passwordsEntered = false;

			return passwordsEntered;
		},
	},
	created() {
		this.code = this.route.query.code;
		if (!this.code) this.$router.push({ name: ROUTE.HOME, query: { msg: MSG_TYPE.FORBIDDEN } });
	},
	mounted() {},
	beforeDestroy() {},
	methods: {
		checkPassword() {
			this.$global.passwordIsValid(this.passwordReset, true);
		},
		checkPasswordRepeat() {
			if (this.passwordReset != this.passwordResetRepeat) this.$global.showToast(TOAST_TYPE.WARN, this.$t('rePasswordsDontMatch'));
		},
		resetPassword() {
			this.isLoading = true;

			this.$network.postData('/api/user/password-reset', { code: this.code, password: this.passwordReset }, null, (err, data) => {
				try {
					if (!err) this.$router.push({ name: ROUTE.HOME, query: { msg: MSG_TYPE.PASSWORD_RESET_SUCCESSFUL } });
					else this.$router.push({ name: ROUTE.HOME, query: { msg: err.msg } });
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.isLoading = false;
				}
			});
		},
	},
};
</script>

<style scoped>
.pr-wrap-content {
	overflow: auto;
	position: relative;
}

.pr-header {
	margin-bottom: 20px;
	font-size: 30px;
	text-align: center;
	font-weight: normal;
}

.pr-wrap-inputs {
	max-width: 400px;
	margin: 10px 0px;
}

.pr-wrap-inputs {
	align-items: center;
	max-width: 400px;
	margin: 10px auto;
}

.pr-wrap-inputs > div {
	margin-bottom: 10px;
}

.pr-wrap-btn {
	width: 100%;
	text-align: center;
}

.pr-wrap-btn button {
	min-width: 200px;
	margin: 10px;
	padding: 10px 20px;
	font-size: 18px;
}

.pr-wrap-password {
	flex: 1 1 200px;
	position: relative;
}

.pr-wrap-password-hint {
	width: calc(100% - 20px);
	padding: 5px 10px;
	position: absolute;
	top: 75px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 10;
	white-space: nowrap;
	border: 1px solid var(--main-color-light);
	border-radius: 5px;
	background-color: var(--main-color-1);
}

.pr-wrap-password-hint p {
	width: 100%;
	margin: 5px 0px;
	display: flex;
	justify-content: center;
	align-items: center;
}

.pr-wrap-password-hint p svg {
	flex: 1 1 25px;
	margin-right: 10px;
	font-size: 20px;
}

.pr-wrap-password-hint p span {
	flex: 1 1 100%;
	max-width: calc(100% - 25px);
	white-space: wrap;
}

.pr-invalid * {
	color: var(--main-color-error);
}

.pr-valid * {
	color: var(--main-color-success);
}

.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
	opacity: 0;
}
.fade-enter-to,
.fade-leave-from {
	opacity: 1;
}
</style>
