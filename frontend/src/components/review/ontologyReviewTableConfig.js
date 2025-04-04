import i18n from '@/translations/i18n.js';
import { global } from '@/scripts/global.js';

const t = i18n.global.t;

export const tableConfig = {
	layout: {
		table: {
			minWidth: '100%',
			maxWidth: '100%',
			minHeight: '100px',
			maxHeight: '300px',
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
			label: t('orSearchReviews'),
			placeholder: t('orSearchReviews'),
		},
		sort: {
			label: t('orSortBy'),
			options: [
				{
					value: 'id-asc',
					text: t('orIDAscSort'),
				},
				{
					value: 'id-desc',
					text: t('orIDDescSort'),
				},
				{
					value: 'submitter-asc',
					text: t('orSubmitterAscSort'),
				},
				{
					value: 'submitter-desc',
					text: t('orSubmitterDescSort'),
				},
				{
					value: 'submissionDate-asc',
					text: t('orSubmissionDateAscSort'),
				},
				{
					value: 'submissionDate-desc',
					text: t('orSubmissionDateDescSort'),
				},
				{
					value: 'reviewer-asc',
					text: t('orReviewerAscSort'),
				},
				{
					value: 'reviewer-desc',
					text: t('orReviewerDescSort'),
				},
				{
					value: 'status-asc',
					text: t('orStatusAscSort'),
				},
				{
					value: 'status-desc',
					text: t('orStatusDescSort'),
				},
			],
			sortMapping: {
				id: ['id'],
				submitter: ['submitter.firstName', 'submitter.lastName'],
				submissionDate: ['submissionDate'],
				reviewer: ['reviewer.firstName', 'reviewer.lastName'],
				status: ['submissionStatus'],
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
				text: t('orID'),
			},
			{
				ref: ['submitter'],
				text: t('orSubmitter'),
				formatter: (submitter) => {
					return `${submitter.firstName} ${submitter.lastName}`;
				},
			},
			{
				ref: ['submitter.role'],
				text: t('orSubmitterRole'),
				formatter: (roles) => {
					return roles.map((it) => t(it)).join(', ');
				},
			},
			{
				ref: ['submissionDate'],
				text: t('orSubmissionDate'),
				formatter: (date) => {
					return global.formatDate(date, 'de');
				},
			},
			{
				ref: ['reviewer'],
				text: t('orReviewer'),
				formatter: (reviewer) => {
					if (reviewer) return `${reviewer.firstName} ${reviewer.lastName}`;
					else return '-';
				},
			},
			{
				ref: ['submissionStatus'],
				text: t('orSubmissionStatus'),
				formatter: (status) => {
					return t(status);
				},
			},
		],
		values: [],
	},
};
