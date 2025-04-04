import i18n from '@/translations/i18n.js';
import { global } from '@/scripts/global.js';
import { TABLE_SELECTION } from '@/enums/enums';
import { mode } from 'd3';

const t = i18n.global.t;

export const dataViewTableConfig = {
	layout: {
		table: {
			minWidth: '100%',
			maxWidth: '100%',
			minHeight: '100px',
			maxHeight: 'calc(100vh - 200px)',
		},
		columns: {
			minWidth: 150,
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
		pagination: {
			itemsPerPage: 25,
		},
	},
	functions: {
		selection: { mode: TABLE_SELECTION.DISABLED },
	},
	data: {
		key: 'rowID',
		columns: [],
		values: [],
	},
};
