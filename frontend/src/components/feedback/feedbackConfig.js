import i18n from '@/translations/i18n.js';
import { global } from '@/scripts/global.js';
import { UPLOAD_TYP, TABLE_SELECTION } from '@/enums/enums';

const t = i18n.global.t;

export const feedbackConfig = {
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
		sort: {
			label: t('fvSortReviews'),
			options: [
				{
					value: 'id-asc',
					text: t('fvIDAscSort'),
				},
				{
					value: 'id-desc',
					text: t('fvIDDescSort'),
				},
				{
					value: 'submissionDate-asc',
					text: t('fvSubmissionDateAscSort'),
				},
				{
					value: 'submissionDate-desc',
					text: t('fvSubmissionDateDescSort'),
				},
				{
					value: 'amount-asc',
					text: t('fvamountCodeBooksAscSort'),
				},
				{
					value: 'amount-desc',
					text: t('fvamountCodeBooksDescSort'),
				},
				{
					value: 'uploadTyp-desc',
					text: t('fvUploadTypDescSort'),
				},
				{
					value: 'uploadTyp-asc',
					text: t('fvUploadTypAscSort'),
				},
				{
					value: 'reviewer-asc',
					text: t('fvReviewerAscSort'),
				},
				{
					value: 'reviewer-desc',
					text: t('fvReviewerDescSort'),
				},
				{
					value: 'status-asc',
					text: t('fvStatusAscSort'),
				},
				{
					value: 'status-desc',
					text: t('fvStatusDescSort'),
				},
			],
			sortMapping: {
				id: ['id'],
				submissionDate: ['submissionDate'],
				amount: ['amountCodeBooks'],
				uploadTyp: ['uploadTyp'],
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
				text: t('fvID'),
			},
			{
				ref: ['submissionDate'],
				text: t('fvSubmissionDate'),
				formatter: (date) => {
					return global.formatDate(date, 'de');
				},
			},
			{
				ref: ['amountCodeBooks'],
				text: t('fvamountCodeBooks'),
			},
			{
				ref: ['uploadTyp'],
				text: t('fvUploadTyp'),
				formatter: (uploadTyp) => {
					switch (uploadTyp) {
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
				text: t('fvReviewer'),
				formatter: (reviewer) => {
					if (reviewer) return `${reviewer.firstName} ${reviewer.lastName}`;
					else return '-';
				},
			},
			{
				ref: ['submissionStatus'],
				text: t('fvSubmissionStatus'),
				formatter: (status) => {
					return t(status);
				},
			},
		],
		values: [],
	},
};
