import i18n from '@/translations/i18n.js';
import { global } from '@/scripts/global.js';

const t = i18n.global.t;

export const studyConfig = {
	layout: {
		table: {
			minWidth: '100%',
			maxWidth: '100%',
			minHeight: '100px',
			maxHeight: '250px',
		},
		columns: {
			minWidth: 50,
			maxWidth: 500,
			padding: {
				top: 10,
				right: 10,
				bottom: 10,
				left: 10,
			},
		},
	},
	header: {
		searchbar: {
			label: t('dvSearchData'),
			placeholder: t('dvSearchData'),
		},
		sort: {
			label: t('dvSortData'),
			options: [
				{
					value: 'id-asc',
					text: t('dvIDAscSort'),
				},
				{
					value: 'id-desc',
					text: t('dvIDDescSort'),
				},
				{
					value: 'name-asc',
					text: t('dvNameAscSort'),
				},
				{
					value: 'name-desc',
					text: t('dvNameDescSort'),
				},
				{
					value: 'submitter-asc',
					text: t('dvSubmitterAscSort'),
				},
				{
					value: 'submitter-desc',
					text: t('dvSubmitterDescSort'),
				},
				{
					value: 'submissionDate-asc',
					text: t('dvSubmissionDateAscSort'),
				},
				{
					value: 'submissionDate-desc',
					text: t('dvSubmissionDateDescSort'),
				},
				{
					value: 'amountQuestionnaire-asc',
					text: t('dvamountQuestionnaireAscSort'),
				},
				{
					value: 'amountQuestionnaire-desc',
					text: t('dvamountQuestionnaireDescSort'),
				},
				{
					value: 'amountData-asc',
					text: t('dvamountDataAscSort'),
				},
				{
					value: 'amountData-desc',
					text: t('dvAmountDescSort'),
				},
			],
			sortMapping: {
				id: ['id'],
				name: ['name'],
				submitter: ['submitter.firstName', 'submitter.lastName'],
				submissionDate: ['submissionDate'],
				amountQuestionnaire: ['amountQuestionnaire'],
				amountData: ['amountData'],
			},
		},
		pagination: {
			itemsPerPage: 10,
		},
	},
	data: {
		key: 'id',
		columns: [
			{
				ref: ['id'],
				text: t('dvID'),
			},
			{
				ref: ['name'],
				text: t('dvName'),
			},
			{
				ref: ['submitter'],
				text: t('dvSubmitter'),
				formatter: (submitter) => {
					return `${submitter.firstName} ${submitter.lastName}`;
				},
			},
			{
				ref: ['submissionDate'],
				text: t('dvSubmissionDate'),
				formatter: (date) => {
					return global.formatDate(date, 'de');
				},
			},
			{
				ref: ['amountQuestionnaire'],
				text: t('dvamountQuestionnaire'),
			},
			{
				ref: ['amountData'],
				text: t('dvamountData'),
			},
		],
		values: [],
	},
};
