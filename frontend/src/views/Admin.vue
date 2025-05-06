<template>
	<div class="ad-wrap-content">
		<div class="ad-wrap-user-table">
			<LoadingSpinner v-if="isLoading" :wrapperClass="'ad-wrap-user-table'" />
			<Table :config="tableConfig" @selectItem="selectUser" />
		</div>
		<div class="ad-wrap-user-edit">
			<UserEdit v-if="selectedUser" :user="selectedUser" @closeUserEdit="selectedUser = null" @reloadUsers="reloadUsers" />
		</div>
	</div>
</template>

<script>
import { TOAST_TYPE } from '@/enums/enums';
import dummyUsers from '@/assets/dummy/users.json';
import { userTableConfig } from '@/components/admin/userTableConfig.js';
import Table from '@/components/general/Table.vue';
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
import UserEdit from '@/components/admin/UserEdit.vue';
/**
 * @vuese
 * @group Admin
 * Wraps all admin functionality
 */
export default {
	name: 'Admin',
	components: { Table, LoadingSpinner, UserEdit },
	emits: [],
	props: {},
	watch: {},
	setup() {
		return {};
	},
	data() {
		return {
			isLoading: false,
			tableConfig: userTableConfig,
			dummyUsers: dummyUsers,
			selectedUser: null,
		};
	},
	computed: {},
	created() {
		this.queryUsers();
	},
	mounted() {},
	beforeDestroy() {},
	methods: {
		queryUsers() {
			this.isLoading = true;

			this.$network.getData('/api/admin/users', null, null, (err, data) => {
				try {
					if (!err) {
						this.tableConfig.data.values = data.map((it) => {
							if (Array.isArray(it.access.role)) it.access.role = it.access.role[0];
							return it;
						});
					} else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.isLoading = false;
				}
			});
		},
		selectUser(user) {
			this.selectedUser = user;
		},
		reloadUsers(reset) {
			if (reset) this.selectedUser = null;

			this.queryUsers();
		},
	},
};
</script>

<style scoped>
.ad-wrap-content {
	width: 100%;
}

.ad-wrap-user-table {
	padding: 10px;
	position: relative;
	overflow: hidden;
}

.ad-wrap-user-edit {
	margin: 20px 0px;
}
</style>
