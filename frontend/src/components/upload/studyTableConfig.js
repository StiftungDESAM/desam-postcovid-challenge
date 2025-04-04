import i18n from '@/translations/i18n.js';
import { global } from '@/scripts/global.js';
import { TABLE_SELECTION } from '@/enums/enums';

const t = i18n.global.t;

export const studyTableConfig = {
	layout: {
		table: {
			minWidth: '100%',
			maxWidth: '100%',
			minHeight: '100px',
			maxHeight: '350px',
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
			label: t('duSearchStudies'),
			placeholder: t('duSearchStudies'),
		},
		sort: {
			label: t('duSortStudies'),
			options: [
				{
					value: 'id-asc',
					text: t('duIDAscSort'),
				},
				{
					value: 'id-desc',
					text: t('duIDDescSort'),
				},
				{
					value: 'name-asc',
					text: t('duNameAscSort'),
				},
				{
					value: 'name-desc',
					text: t('duNameDescSort'),
				},
				{
					value: 'purpose-asc',
					text: t('duPurposeAscSort'),
				},
				{
					value: 'purpose-desc',
					text: t('duPurposeDescSort'),
				},
				{
					value: 'timeframe-asc',
					text: t('duTimeframeAscSort'),
				},
				{
					value: 'timeframe-desc',
					text: t('duTimeframeDescSort'),
				},
				{
					value: 'submitter-asc',
					text: t('duSubmitterAscSort'),
				},
				{
					value: 'submitter-desc',
					text: t('duSubmitterDescSort'),
				},
				{
					value: 'submissionDate-asc',
					text: t('duSubmissionDateAscSort'),
				},
				{
					value: 'submissionDate-desc',
					text: t('duSubmissionDateDescSort'),
				},
				{
					value: 'amount-asc',
					text: t('duamountCodeBooksAscSort'),
				},
				{
					value: 'amount-desc',
					text: t('duamountCodeBooksDescSort'),
				},
			],
			sortMapping: {
				id: ['id'],
				name: ['name'],
				purpose: ['purpose'],
				timeframe: ['dateStart', 'dateEnd'],
				submitter: ['submitter.firstName', 'submitter.lastName'],
				submissionDate: ['submissionDate'],
				amount: ['amountCodeBooks'],
			},
		},
		pagination: {
			itemsPerPage: 10,
		},
	},
	functions: {
		selection: {
			mode: TABLE_SELECTION.ROW_SELECT,
		},
	},
	data: {
		key: 'id',
		columns: [
			{
				ref: ['id'],
				text: t('duID'),
			},
			{
				ref: ['name'],
				text: t('duName'),
			},
			{
				ref: ['purpose'],
				text: t('duPurpose'),
				formatter: (purpose) => {
					return t(purpose);
				},
			},
			{
				ref: ['dateStart', 'dateEnd'],
				text: t('duTimeframe'),
				formatter: (dateStart, dateEnd) => {
					return `${global.formatDate(dateStart, 'de', true)} - ${global.formatDate(dateEnd, 'de', true)}`;
				},
			},
			{
				ref: ['submitter'],
				text: t('duSubmitter'),
				formatter: (submitter) => {
					return `${submitter.firstName} ${submitter.lastName}`;
				},
			},
			{
				ref: ['submissionDate'],
				text: t('duSubmissionDate'),
				formatter: (date) => {
					return global.formatDate(date, 'de');
				},
			},
			{
				ref: ['amountCodeBooks'],
				text: t('duamountCodeBooks'),
			},
		],
		values: [],
	},
};
