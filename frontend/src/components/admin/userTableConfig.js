import i18n from '@/translations/i18n.js';
const t = i18n.global.t;

export const userTableConfig = {
	layout: {
		table: {
			maxHeight: '60vh',
		},
		columns: {
			minWidth: 100,
			maxWidth: 700,
		},
	},
	header: {
		searchbar: {
			label: t('utSearchUsers'),
			placeholder: t('utSearchUsers'),
		},
		sort: {
			label: t('utSortBy'),
			options: [
				{
					value: 'name-asc',
					text: t('utNameAscSort'),
				},
				{
					value: 'name-desc',
					text: t('utNameDescSort'),
				},
				{
					value: 'gender-asc',
					text: t('utGenderAscSort'),
				},
				{
					value: 'gender-desc',
					text: t('utGenderDescSort'),
				},
				{
					value: 'dateOfBirth-asc',
					text: t('utDateOfBirthAscSort'),
				},
				{
					value: 'dateOfBirth-desc',
					text: t('utDateOfBirthDescSort'),
				},
				{
					value: 'role-asc',
					text: t('utRoleAscSort'),
				},
				{
					value: 'role-desc',
					text: t('utRoleDescSort'),
				},
				{
					value: 'email-asc',
					text: t('utEmailAscSort'),
				},
				{
					value: 'email-desc',
					text: t('utEmailDescSort'),
				},
				{
					value: 'accountVerification-asc',
					text: t('utVerificationStatusAscSort'),
				},
				{
					value: 'accountVerification-desc',
					text: t('utVerificationStatusDescSort'),
				},
			],
			sortMapping: {
				name: ['user.firstName', 'user.lastName'],
				gender: ['user.gender'],
				dateOfBirth: ['user.dateOfBirth'],
				role: ['access.role'],
				email: ['credentials.email'],
				accountVerification: ['accountVerification'],
			},
		},
		pagination: {
			itemsPerPage: 10,
		},
	},
	data: {
		key: 'credentials.email',
		columns: [
			{
				ref: ['user.firstName'],
				text: t('utFirstName'),
			},
			{
				ref: ['user.lastName'],
				text: t('utLastName'),
			},
			{
				ref: ['user.gender'],
				text: t('utGender'),
				formatter: (gender) => {
					return t(gender);
				},
			},
			{
				ref: ['user.dateOfBirth'],
				text: t('utDateOfBirth'),
			},
			{
				ref: ['access.role'],
				text: t('utRole'),
				formatter: (role) => {
					return t(role);
				},
			},
			{
				ref: ['access.permissionsGranted'],
				text: t('utPermissions'),
				formatter: (permissions) => {
					return permissions.length > 0 ? permissions.map((it) => t(it)).join(', ') : '-';
				},
			},
			{
				ref: ['credentials.email'],
				text: t('utEmail'),
			},
			{
				ref: ['accountVerification'],
				text: t('utVerificationStatus'),
				formatter: (status) => {
					return t(status);
				},
			},
		],
		values: [],
	},
};
