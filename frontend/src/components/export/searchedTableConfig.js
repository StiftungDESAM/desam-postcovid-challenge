import i18n from '@/translations/i18n.js';
import { TABLE_SELECTION, TABLE_SELECTION_AMOUNT } from '@/enums/enums';

const t = i18n.global.t;

export const searchedTableConfig = {
	layout: {
		table: {
			minWidth: '100%',
			maxWidth: '100%',
			minHeight: '100px',
			maxHeight: '500px',
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
			label: t('deSearchData'),
			placeholder: t('deSearchData'),
		},
		pagination: {
			itemsPerPage: 25,
		},
	},
	functions: {
		selection: {
			mode: TABLE_SELECTION.ROW,
			amount: TABLE_SELECTION_AMOUNT.MULTIPLE,
		},
	},
	data: {
		key: 'id',
		columns: [],
		values: [],
	},
};
