# Table

Generic table component Config structure: { layout: { table: { minWidth: String // The min width of the table. The unit (px,%,...) will be defined in the string itself maxWidth: String // The max width of the table. The unit (px,%,...) will be defined in the string itself minHeight: String // The min height of the table. The unit (px,%,...) will be defined in the string itself maxHeight: String // The max height of the table. The unit (px,%,...) will be defined in the string itself }, columns:{ minWidth: Number // The min width of the table column in px. Default is 100 maxWidth: Number // The max width of the table column in px. Default is 750 padding: { // The padding values for the columns. Will be 15px for all by default top: Number, // The top padding of the column right: Number, // The right padding of the column bottom: Number, // The bottom padding of the column left: Number, // The left padding of the column } } }, header: { searchbar: { // If false or undefined the searchbar wont be rendered label: String, // Text label for the search input field placeholder: String, // Placeholder text displayed inside the search input }, sort: { // If false or undefined the sort by wont be rendered label: String, // Label for the sorting dropdown options: [ { value: String, // Value of the sort option. Must follow this pattern: <key>-<sortDirection> e.g name-desc text: String  // Displayed text for the sort option }, ], sortMapping: [ // Maps certain properties of the data to the sort option { key: [String] // Replace key with the name of the key from the sort options. Holds at least one String that is the key to a data property. e.g name: ['user.firstName', 'user.lastName'] } ] }, pagination: { // If false or undefined the pagination wont be rendered itemsPerPage: Number, // Specifies how many items to display per page }, }, functions:{ selection:{ mode: String, // Defines how the user click selection works. Can be ROW_SELECT for rows, COLUMN_SELECT for columns or DISABLED it no selection should be allowed. Default is ROW_SELECT amount: String // Defines how many rows of columns can be selected. Can be SINGLE or MULTIPLE. Default is SINGLE } columns:{ delete: Boolean // If true displays a delete icon for a certain column edit: Boolean // If true displays a edit icon for a certain column header tha can be used to change the header text }, rows:{ delete: Boolean // If true displays a delete icon for a certain row }, cells:{ }, }, styling: { // Styling options for the table customClasses: [ // Array of custom classes that can be passed. Need to be in a style tag without scope { // If both colRef and rowRef are set then the cell will be targeted className: "String", // Name of the class colRef: "String", // Ref of the column. If set alone will target the whole column rowRef: "String" // Ref of the row. If set alone will target the whole row } ] }, data: { key: String // Identifier for the item in the passed data array. Needs to be unique columns: [ { ref: ['String'], // Property that contains an array of values (e.g. ['dateStart', 'dateEnd']) text: String, // Column name formatter: Function?, // Optional converter that parses the data a certain way }, ], values: [ Object // The data for the table rows. Must match the provided columns and ref structure ] }, }

## Props

<!-- @vuese:Table:props:start -->
|Name|Description|Type|Required|Default|
|---|---|---|---|---|
|config|-|`Object`|`true`|-|
|resetSelected|-|`Boolean`|`false`|-|
|startValue|-|`String` /  `Number`|`false`|-|

<!-- @vuese:Table:props:end -->


## Events

<!-- @vuese:Table:events:start -->
|Event Name|Description|Parameters|
|---|---|---|
|selectItem|-|-|
|deleteColumn|-|-|
|deleteRow|-|-|

<!-- @vuese:Table:events:end -->


