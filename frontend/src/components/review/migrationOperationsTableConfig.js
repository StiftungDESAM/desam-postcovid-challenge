import i18n from '@/translations/i18n.js';
import { global } from '@/scripts/global.js';

const t = i18n.global.t;

export const tableConfig = {
	layout: {
		table: {
			minWidth: '100%',
			maxWidth: '100%',
			minHeight: '100px',
			maxHeight: '400px',
		},
		columns: {
			minWidth: 50,
			maxWidth: 500,
			padding: {
				top: 10,
				right: 15,
				bottom: 10,
				left: 15,
			},
		},
	},
	header: null,
	data: {
		key: 'id',
		columns: [
			{
				ref: ['id'],
				text: t('moID'),
			},
			{
				ref: ['operation.main'],
				text: t('moMainOperation'),
			},
			{
				ref: ['operation.sub'],
				text: t('moSubOperation'),
				formatter: (sub) => {
					return sub ? sub : '-';
				},
			},
			{
				ref: ['elementType'],
				text: t('moElementType'),
				formatter: (elementType) => {
					return t(elementType);
				},
			},
			{
				ref: ['tag'],
				text: t('moTag'),
			},
			{
				ref: ['name'],
				text: t('moName'),
			},
		],
		values: [],
	},
};
