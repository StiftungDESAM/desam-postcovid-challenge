import i18n from '@/translations/i18n.js';
import { TABLE_SELECTION } from '@/enums/enums';

const t = i18n.global.t;

export const dataTableConfig = {
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
			label: t('duSearchData'),
			placeholder: t('duSearchData'),
		},
		pagination: {
			itemsPerPage: 25,
		},
	},
	functions: {
		selection: {
			mode: TABLE_SELECTION.COLUMN_SELECT,
		},
		rows: {
			delete: true,
		},
	},
	data: {
		key: 'rowID',
		columns: [],
		values: [],
	},
};
