import i18n from '@/translations/i18n.js';
import { global } from '@/scripts/global.js';
import { UPLOAD_TYP, TABLE_SELECTION } from '@/enums/enums';

const t = i18n.global.t;

export const submissionsConfig = {
	layout: {
		table: {
			minWidth: '100%',
			maxWidth: '100%',
			minHeight: '100px',
			maxHeight: '70vh',
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
			label: t('prSearchSubmissions'),
			placeholder: t('prSearchSubmissions'),
		},
		sort: {
			label: t('prSortSubmissions'),
			options: [
				{
					value: 'id-asc',
					text: t('prIDAscSort'),
				},
				{
					value: 'id-desc',
					text: t('prIDDescSort'),
				},
				{
					value: 'name-asc',
					text: t('prNameAscSort'),
				},
				{
					value: 'name-desc',
					text: t('prNameDescSort'),
				},
				{
					value: 'purpose-asc',
					text: t('prPurposeAscSort'),
				},
				{
					value: 'purpose-desc',
					text: t('prPurposeDescSort'),
				},
				{
					value: 'timeframe-asc',
					text: t('prTimeframeAscSort'),
				},
				{
					value: 'timeframe-desc',
					text: t('prTimeframeDescSort'),
				},
				{
					value: 'submissionDate-asc',
					text: t('prSubmissionDateAscSort'),
				},
				{
					value: 'submissionDate-desc',
					text: t('prSubmissionDateDescSort'),
				},
				{
					value: 'amount-asc',
					text: t('pramountCodeBooksAscSort'),
				},
				{
					value: 'amount-desc',
					text: t('pramountCodeBooksDescSort'),
				},
				{
					value: 'uploadType-desc',
					text: t('prUploadTypDescSort'),
				},
				{
					value: 'uploadType-asc',
					text: t('prUploadTypAscSort'),
				},
				{
					value: 'reviewer-asc',
					text: t('prReviewerAscSort'),
				},
				{
					value: 'reviewer-desc',
					text: t('prReviewerDescSort'),
				},
				{
					value: 'status-asc',
					text: t('prStatusAscSort'),
				},
				{
					value: 'status-desc',
					text: t('prStatusDescSort'),
				},
			],
			sortMapping: {
				id: ['id'],
				name: ['name'],
				purpose: ['purpose'],
				timeframe: ['dateStart', 'dateEnd'],
				submissionDate: ['submissionDate'],
				amount: ['amountCodeBooks'],
				uploadType: ['uploadType'],
				reviewer: ['reviewer.firstName', 'reviewer.lastName'],
				status: ['submissionStatus'],
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
				text: t('prID'),
			},
			{
				ref: ['name'],
				text: t('prName'),
			},
			{
				ref: ['purpose'],
				text: t('prPurpose'),
				formatter: (purpose) => {
					if (purpose) return t(purpose);
					else return t('prOntologyUpload');
				},
			},
			{
				ref: ['dateStart', 'dateEnd'],
				text: t('prTimeframe'),
				formatter: (dateStart, dateEnd) => {
					if (dateStart && dateEnd) return `${global.formatDate(dateStart, 'de', true)} - ${global.formatDate(dateEnd, 'de', true)}`;
					else return '-';
				},
			},
			{
				ref: ['submissionDate'],
				text: t('prSubmissionDate'),
				formatter: (date) => {
					return global.formatDate(date, 'de');
				},
			},
			{
				ref: ['amountCodeBooks'],
				text: t('pramountCodeBooks'),
			},
			{
				ref: ['uploadType'],
				text: t('uploadType'),
				formatter: (uploadType) => {
					switch (uploadType) {
						case UPLOAD_TYP.UPLOAD_DATA:
							return t('UPLOAD_DATA');
						case UPLOAD_TYP.UPLOAD_ONTOLOGY:
							return t('UPLOAD_ONTOLOGY');
						default:
							return '-';
					}
				},
			},
			{
				ref: ['reviewer'],
				text: t('prReviewer'),
				formatter: (reviewer) => {
					if (reviewer) return `${reviewer.firstName} ${reviewer.lastName}`;
					else return '-';
				},
			},
			{
				ref: ['submissionStatus'],
				text: t('prSubmissionStatus'),
				formatter: (status) => {
					return t(status);
				},
			},
		],
		values: [],
	},
};
