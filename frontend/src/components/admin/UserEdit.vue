<template>
	<div class="ue-wrap-content">
		<LoadingSpinner v-if="isLoading" :wrapperClass="'ue-wrap-content'" />
		<ConfirmationWindow v-if="confirmationConfig" :config="confirmationConfig" />
		<div class="ue-wrap-general">
			<h2>{{ $t('ueGeneralInformation') }}</h2>
			<div class="ue-wrap-general-fields">
				<InputField v-model="modifiedUser.user.firstName" :placeholder="$t('ueFirstName')" :labelText="$t('ueFirstName')" />
				<InputField v-model="modifiedUser.user.lastName" :placeholder="$t('ueLastName')" :labelText="$t('ueLastName')" />
				<InputField v-model="modifiedUser.user.dateOfBirth" :labelText="$t('ueDateOfBirth')" :inputType="'date'" @newValue="checkDOB" />
				<SelectField
					v-model="modifiedUser.user.gender"
					:placeholder="$t('ueSelectGender')"
					:labelText="$t('ueGender')"
					:options="genderOptions"
				/>
			</div>
		</div>
		<div class="ue-wrap-access">
			<h2>{{ $t('ueAccessInformation') }}</h2>
			<div class="ue-wrap-access-fields">
				<div class="ue-wrap-functionalities">
					<p>{{ $t('ueRequestedFunctionalities') }}</p>
					<div class="ue-wrap-user-checkboxes">
						<InputField
							v-for="permission in permissions"
							:key="permission"
							v-model="modifiedUser.access.permissionsRequested[permission]"
							:labelText="$t(permission)"
							:inputType="'checkbox'"
							:disabled="true"
						/>
					</div>
					<p>
						{{ $t('ueGrantedFunctionalities') }}
						<span>({{ $t(modifiedUser.permissionVerification == enumVERIFICATION.NOT_VERIFIED ? 'ueUnverified' : 'ueVerified') }})</span>
					</p>
					<div class="ue-wrap-user-checkboxes">
						<InputField
							v-for="permission in permissions"
							:key="permission"
							v-model="modifiedUser.access.permissionsGranted[permission]"
							:labelText="$t(permission)"
							:inputType="'checkbox'"
							:disabled="user.access.role == enumROLE.SUPER_ADMIN"
						/>
					</div>
					<button
						v-if="modifiedUser.permissionVerification == enumVERIFICATION.NOT_VERIFIED"
						class="app-default-btn"
						@click="confirmPermissionVerification"
					>
						{{ $t('ueVerifyScopes') }} <fai icon="fas fa-circle-check" />
					</button>
				</div>
				<div class="ue-wrap-user-role">
					<SelectField
						v-model="modifiedUser.access.role"
						:placeholder="$t('ueSelectRole')"
						:labelText="$t('ueRole')"
						:options="roleOptions"
						:disabled="modifiedUser.access.role == enumROLE.SUPER_ADMIN"
					/>
				</div>
			</div>
		</div>
		<div class="ue-wrap-user">
			<h2>{{ $t('ueUserInformation') }}</h2>
			<div class="ue-wrap-user-fields">
				<InputField v-model="user.credentials.email" :placeholder="$t('ueEmail')" :labelText="$t('ueEmail')" :disabled="true" />
				<SelectField
					v-model="user.accountVerification"
					:placeholder="$t('ueSelectVerificationStatus')"
					:labelText="$t('ueVerificationStatus')"
					:options="accountVerificationOptions"
					:disabled="user.access.role == enumROLE.SUPER_ADMIN"
				/>
				<button class="app-default-btn" @click="confirmResendVerificationEmail">
					{{ $t('ueResendVerificationEmail') }} <fai icon="fas fa-envelope" />
				</button>
				<button :class="user.access.role == enumROLE.SUPER_ADMIN ? 'app-disabled-btn' : 'app-warn-btn'" @click="confirmResetPassword">
					{{ $t('ueRequestPasswordReset') }} <fai icon="fas fa-key" />
				</button>
				<button :class="user.access.role == enumROLE.SUPER_ADMIN ? 'app-disabled-btn' : 'app-error-btn'" @click="confirmDeleteUser">
					{{ $t('ueDeleteUser') }} <fai icon="fas fa-user-xmark" />
				</button>
			</div>
		</div>

		<div class="ue-wrap-btn">
			<button class="app-warn-btn" @click="$emit('closeUserEdit')">{{ $t('ueDiscardChanges') }} <fai icon="fas fa-rotate-left" /></button>
			<button :class="allInformationValid ? 'app-success-btn' : 'app-disabled-btn'" @click="updateUser">
				{{ $t('ueSaveChanges') }} <fai icon="fas fa-paper-plane" />
			</button>
		</div>
	</div>
</template>

<script>
import { GENDER, ROLE, PERMISSION, VERIFICATION_STATUS, TOAST_TYPE } from '@/enums/enums';
import InputField from '@/components/general/InputField.vue';
import SelectField from '@/components/general/SelectField.vue';
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
import ConfirmationWindow from '@/components/general/ConfirmationWindow.vue';
/**
 * @vuese
 * @group Admin
 * Editable user element
 */
export default {
	name: 'UserEdit',
	components: { InputField, SelectField, LoadingSpinner, ConfirmationWindow },
	emits: ['closeUserEdit', 'reloadUsers'],
	props: {
		user: {
			type: Object,
			required: true,
		},
	},
	watch: {
		user: {
			handler: function (newVal) {
				this.setupModifiedUser();
			},
			deep: true,
		},
	},
	setup() {
		const enumROLE = ROLE;
		const enumVERIFICATION = VERIFICATION_STATUS;

		return { enumROLE, enumVERIFICATION };
	},
	data() {
		return {
			isLoading: false,
			currentUser: this.$store.getCurrentUser(),
			genderOptions: Object.values(GENDER),
			accountVerificationOptions: Object.values(VERIFICATION_STATUS),
			permissions: Object.values(PERMISSION).filter((it) => it != PERMISSION.SUPER_ADMIN),
			modifiedUser: JSON.parse(JSON.stringify(this.user)),
			confirmationConfig: null,
		};
	},
	computed: {
		roleOptions() {
			return Object.values(ROLE).filter(
				(it) => it != ROLE.SUPER_ADMIN || (it == ROLE.SUPER_ADMIN && this.user.access.role == ROLE.SUPER_ADMIN)
			);
		},
		userInfoChanged() {
			let infoChanged = false;

			if (this.user.user.firstName != this.modifiedUser.user.firstName) infoChanged = true;
			else if (this.user.user.lastName != this.modifiedUser.user.lastName) infoChanged = true;
			else if (this.user.user.dateOfBirth != this.modifiedUser.user.dateOfBirth) infoChanged = true;
			else if (this.user.user.gender != this.modifiedUser.user.gender) infoChanged = true;
			else if (this.user.access.role != this.modifiedUser.access.role) infoChanged = true;
			else if (this.user.accountVerification != this.modifiedUser.accountVerification) infoChanged = true;
			else if (this.user.access.permissionsGranted.length != this.modifiedUser.access.permissionsGranted.length) infoChanged = true;
			else {
				const sortedInitialPermissions = [...this.user.access.permissionsGranted].sort();
				const sortedModifiedPermissions = [...this.modifiedUser.access.permissionsGranted].sort();

				for (let i = 0; i < sortedInitialPermissions.length; i++)
					if (sortedInitialPermissions[i] !== sortedModifiedPermissions[i]) infoChanged = true;
			}

			return infoChanged;
		},
		allInformationValid() {
			let allInfoValid = true;

			if (!this.modifiedUser.user.firstName) allInfoValid = false;
			else if (!this.modifiedUser.user.lastName) allInfoValid = false;
			else if (!this.$global.dobIsValid(this.modifiedUser.user.dateOfBirth)) allInfoValid = false;
			else if (!this.modifiedUser.user.gender) allInfoValid = false;
			else if (!this.modifiedUser.access.role) allInfoValid = false;

			return allInfoValid && this.userInfoChanged;
		},
	},
	created() {
		this.setupModifiedUser();
	},
	mounted() {},
	beforeDestroy() {},
	methods: {
		setupModifiedUser() {
			this.modifiedUser = JSON.parse(JSON.stringify(this.user));
			this.modifiedUser.access.permissionsRequested = {};
			this.user.access.permissionsRequested.forEach((it) => {
				this.modifiedUser.access.permissionsRequested[it] = true;
			});

			if (this.modifiedUser.permissionVerification == VERIFICATION_STATUS.NOT_VERIFIED && this.user.access.permissionsGranted.length == 0) {
				this.modifiedUser.access.permissionsGranted = JSON.parse(JSON.stringify(this.modifiedUser.access.permissionsRequested));
			} else {
				this.modifiedUser.access.permissionsGranted = {};
				this.user.access.permissionsGranted.forEach((it) => {
					this.modifiedUser.access.permissionsGranted[it] = true;
				});
			}
		},
		checkDOB(dob) {
			if (dob && !dob.startsWith('0') && !this.$global.dobIsValid(dob)) this.$global.showToast(TOAST_TYPE.WARN, this.$t('reInvalidDate'));
		},
		confirmResendVerificationEmail() {
			this.confirmationConfig = {
				title: this.$t('ueResendVerificationEmail'),
				text: this.$t('ueResendVerificationEmailText'),
				cancelButton: {
					class: 'app-default-btn',
					text: this.$t('ueCancel'),
					callback: () => {
						this.isLoading = false;
						this.confirmationConfig = null;
					},
				},
				confirmButton: {
					class: 'app-success-btn',
					text: this.$t('ueResendVerificationEmail'),
					callback: () => {
						this.confirmationConfig = null;
						this.resendVerificationEmail();
					},
				},
			};
		},
		resendVerificationEmail() {
			this.isLoading = true;

			this.$network.postData(`/api/admin/users/${this.user.credentials.email}/resend-verification`, null, null, (err, data) => {
				try {
					if (!err) this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('ueVerificationEmailResent'));
					else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.isLoading = false;
				}
			});
		},
		confirmResetPassword() {
			this.confirmationConfig = {
				title: this.$t('ueResetUserPasswordTitle'),
				text: this.$t('ueResetUserPasswordText'),
				cancelButton: {
					class: 'app-default-btn',
					text: this.$t('ueCancel'),
					callback: () => {
						this.isLoading = false;
						this.confirmationConfig = null;
					},
				},
				confirmButton: {
					class: 'app-warn-btn',
					text: this.$t('ueRequestPasswordReset'),
					callback: () => {
						this.confirmationConfig = null;
						this.requestPasswordReset();
					},
				},
			};
		},
		requestPasswordReset() {
			this.isLoading = true;

			this.$network.postData(`/api/admin/users/${this.user.credentials.email}/request-password-reset`, null, null, (err, data) => {
				try {
					if (!err) this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('ueResetEmailSent'));
					else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.isLoading = false;
				}
			});
		},
		confirmPermissionVerification() {
			this.confirmationConfig = {
				title: this.$t('usVerifyPermissionsTitle'),
				text: this.$t('usVerifyPermissionsText'),
				cancelButton: {
					class: 'app-default-btn',
					text: this.$t('ueCancel'),
					callback: () => {
						this.confirmationConfig = null;
					},
				},
				confirmButton: {
					class: 'app-success-btn',
					text: this.$t('usVerifyPermissions'),
					callback: () => {
						this.confirmationConfig = null;
						this.verifyPermissions();
					},
				},
			};
		},
		verifyPermissions() {
			this.isLoading = true;

			const permissions = Object.keys(this.modifiedUser.access.permissionsRequested).filter(
				(key) => this.modifiedUser.access.permissionsRequested[key]
			);

			this.$network.postData(
				`/api/admin/users/${this.user.credentials.email}/verify-permissions`,
				{ permissions: permissions },
				null,
				(err, data) => {
					try {
						if (!err) {
							this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('uePermissionsVerified'));
							this.modifiedUser.permissionVerification = VERIFICATION_STATUS.VERIFIED;
							this.$emit('reloadUsers', false);
						} else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
					} catch (error) {
						this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
					} finally {
						this.isLoading = false;
					}
				}
			);
		},
		confirmDeleteUser() {
			this.confirmationConfig = {
				title: this.$t('ueDeleteUserTitle'),
				text: this.$t('ueDeleteUserText'),
				cancelButton: {
					class: 'app-default-btn',
					text: this.$t('ueCancel'),
					callback: () => {
						this.isLoading = false;
						this.confirmationConfig = null;
					},
				},
				confirmButton: {
					class: 'app-error-btn',
					text: this.$t('ueDeleteUser'),
					callback: () => {
						this.confirmationConfig = null;
						this.deleteUser();
					},
				},
			};
		},
		deleteUser() {
			this.isLoading = true;

			this.$network.deleteData(`/api/admin/users/${this.user.credentials.email}`, null, null, (err, data) => {
				try {
					if (!err) {
						this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('ueUserDeleted'));
						this.$emit('reloadUsers', true);
					} else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.isLoading = false;
				}
			});
		},
		updateUser() {
			this.isLoading = true;

			let user = JSON.parse(JSON.stringify(this.modifiedUser));
			user.access.role = [user.access.role];
			user.access.permissionsRequested = Object.keys(user.access.permissionsRequested).filter((key) => user.access.permissionsRequested[key]);
			user.access.permissionsGranted = Object.keys(user.access.permissionsGranted).filter((key) => user.access.permissionsGranted[key]);

			this.$network.patchData(`/api/admin/users/${user.credentials.email}`, user, null, (err, data) => {
				try {
					if (!err) {
						this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('ueUpdatedUserSuccessfully'));
						this.$emit('reloadUsers', false);
					} else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
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
.ue-wrap-content {
	width: 100%;
	position: relative;
}

.ue-wrap-general,
.ue-wrap-user,
.ue-wrap-access {
	width: 100%;
	margin: 10px 0px;
}

.ue-wrap-general-fields,
.ue-wrap-access-fields {
	display: flex;
	justify-content: flex-start;
	align-items: flex-start;
	flex-flow: wrap;
}

.ue-wrap-user-fields {
	display: flex;
	justify-content: center;
	align-items: flex-end;
	flex-flow: wrap;
}

.ue-wrap-general h2,
.ue-wrap-user h2,
.ue-wrap-access h2 {
	margin-bottom: 10px;
	font-size: 20px;
	text-decoration: underline;
	font-weight: normal;
}

.ue-wrap-functionalities {
	flex: 1 1 calc(100% - 400px);
	margin: 0px 10px;
}

.ue-wrap-functionalities p {
	margin: 10px 0px;
}

.ue-wrap-functionalities button {
	margin: 10px 5px;
	padding: 10px 15px;
	font-size: 17px;
}

.ue-wrap-user-checkboxes {
	display: flex;
	justify-content: flex-start;
	align-items: flex-start;
	flex-flow: wrap;
}

.ue-wrap-user-checkboxes > div {
	max-width: 200px;
}

.ue-wrap-user-role {
	flex: 1 1 200px;
}

.ue-wrap-btn {
	width: 100%;
	text-align: center;
}

.ue-wrap-btn button,
.ue-wrap-user-fields button {
	min-width: 200px;
	height: 40px;
	margin: 5px;
	font-size: 16px;
}
</style>
