import i18n from '@/translations/i18n.js';
import { TABLE_SELECTION, UPLOAD_TYP } from '@/enums/enums';

const t = i18n.global.t;

export const feedbackCodebookTableConfig = {
	layout: {
		table: {
			minWidth: '100%',
			maxWidth: '100%',
			minHeight: '100px',
			maxHeight: 'calc(100vh - 200px)',
		},
		columns: {
			minWidth: 200,
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
			label: t('fvSearchCodebook'),
			placeholder: t('fvSearchCodebook'),
		},
		pagination: {
			itemsPerPage: 10,
		},
	},
	functions: {
		selection: {
			mode: TABLE_SELECTION.DISABLED,
		},
	},
	data: {
		key: 'rowID',
		columns: [],
		values: [],
	},
};
